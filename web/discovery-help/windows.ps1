# Local IPv4 mDNS only; no downloads, administrator rights or device changes.
# Paste the complete block in Windows PowerShell or PowerShell.
& {
$ErrorActionPreference = 'Stop'
if (-not ('Hue2LoxLocalDiscovery' -as [type])) {
Add-Type -TypeDefinition @'
using System;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Text;
public static class Hue2LoxLocalDiscovery {
    const string Service = "_hue._tcp.local";
    public class Records {
        public HashSet<string> Instances = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
        public Dictionary<string,string> Targets = new Dictionary<string,string>(StringComparer.OrdinalIgnoreCase);
        public Dictionary<string,string> Addresses = new Dictionary<string,string>(StringComparer.OrdinalIgnoreCase);
    }
    static int U16(byte[] b, int p) {
        if (p < 0 || p + 2 > b.Length) throw new FormatException();
        return (b[p] << 8) | b[p+1];
    }
    static string Name(byte[] b, ref int offset) {
        int p=offset, end=-1;
        var labels=new List<string>(); var seen=new HashSet<int>();
        for (int step=0; step<128; step++) {
            if (p>=b.Length || !seen.Add(p)) throw new FormatException();
            int n=b[p++];
            if (n==0) { offset=end<0?p:end; return String.Join(".",labels); }
            if ((n&192)==192) {
                if(p>=b.Length) throw new FormatException();
                if(end<0) end=p+1;
                p=((n&63)<<8)|b[p]; continue;
            }
            if(n>63 || p+n>b.Length) throw new FormatException();
            labels.Add(Encoding.UTF8.GetString(b,p,n)); p+=n;
        }
        throw new FormatException();
    }
    public static void Parse(byte[] b, Records result) {
        // Parse into a temporary result: malformed packets never partially update state.
        if(b.Length<12 || b.Length>9000 || (b[2]&128)==0) throw new FormatException();
        int questions=U16(b,4), count=U16(b,6)+U16(b,8)+U16(b,10), p=12;
        if(questions>256 || count>256) throw new FormatException();
        var found=new Records();
        for(int i=0;i<questions;i++) { Name(b,ref p); p+=4; if(p>b.Length) throw new FormatException(); }
        for(int i=0;i<count;i++) {
            string owner=Name(b,ref p);
            int type=U16(b,p), cls=U16(b,p+2)&32767, size=U16(b,p+8);
            bool alive=(b[p+4]|b[p+5]|b[p+6]|b[p+7])!=0;
            p+=10; int end=p+size; if(end>b.Length) throw new FormatException();
            if(cls==1 && alive) {
                int q=p;
                if(type==12 && owner.Equals(Service,StringComparison.OrdinalIgnoreCase)) {
                    string instance=Name(b,ref q); if(q>end) throw new FormatException();
                    if(instance.EndsWith("."+Service,StringComparison.OrdinalIgnoreCase)) found.Instances.Add(instance);
                } else if(type==33 && size>=7) {
                    q+=6; string target=Name(b,ref q); if(q>end) throw new FormatException();
                    found.Targets[owner]=target;
                } else if(type==1 && size==4) {
                    byte a=b[p], c=b[p+1];
                    if(a==10 || (a==172 && c>=16 && c<=31) || (a==192 && c==168))
                        found.Addresses[owner]=String.Format("{0}.{1}.{2}.{3}",a,c,b[p+2],b[p+3]);
                }
            }
            p=end;
        }
        foreach(var v in found.Instances) result.Instances.Add(v);
        foreach(var v in found.Targets) result.Targets[v.Key]=v.Value;
        foreach(var v in found.Addresses) result.Addresses[v.Key]=v.Value;
    }
    public static byte[] Query(string name, int type) {
        using(var m=new MemoryStream()) {
            m.Write(new byte[]{0,0,0,0,0,1,0,0,0,0,0,0},0,12);
            foreach(string label in name.Split('.')) {
                byte[] b=Encoding.UTF8.GetBytes(label);
                if(b.Length==0 || b.Length>63) throw new FormatException();
                m.WriteByte((byte)b.Length); m.Write(b,0,b.Length);
            }
            m.WriteByte(0); m.WriteByte((byte)(type>>8)); m.WriteByte((byte)type);
            m.WriteByte(128); m.WriteByte(1); // Ask for a unicast reply to this socket.
            return m.ToArray();
        }
    }
    public static string[] Find() {
        var result=new Records(); var asked=new HashSet<string>();
        using(var udp=new UdpClient(new IPEndPoint(IPAddress.Any,0))) {
            udp.Client.ReceiveTimeout=200;
            udp.Client.SetSocketOption(SocketOptionLevel.IP,SocketOptionName.MulticastTimeToLive,255);
            var multicast=new IPEndPoint(IPAddress.Parse("224.0.0.251"),5353);
            byte[] first=Query(Service,12); udp.Send(first,first.Length,multicast);
            DateTime until=DateTime.UtcNow.AddSeconds(6); int packets=0;
            while(DateTime.UtcNow<until && packets<256) {
                try {
                    IPEndPoint sender=new IPEndPoint(IPAddress.Any,0);
                    byte[] b=udp.Receive(ref sender); packets++;
                    if(sender.Port==5353) { try { Parse(b,result); } catch(FormatException) {} }
                } catch(SocketException e) {
                    if(e.SocketErrorCode!=SocketError.TimedOut && e.SocketErrorCode!=SocketError.WouldBlock) throw;
                }
                foreach(string instance in result.Instances) {
                    string target;
                    string query=instance; int type=33;
                    if(result.Targets.TryGetValue(instance,out target)) { query=target; type=1; }
                    if(asked.Count<128 && asked.Add(query)) {
                        byte[] b=Query(query,type); udp.Send(b,b.Length,multicast);
                    }
                }
            }
        }
        var lines=new SortedSet<string>();
        foreach(string instance in result.Instances) {
            string target, address;
            if(result.Targets.TryGetValue(instance,out target) && result.Addresses.TryGetValue(target,out address)) {
                string label=instance.Substring(0,instance.Length-Service.Length-1);
                var safe=new StringBuilder(); foreach(char c in label) safe.Append(Char.IsControl(c)?'?':c);
                lines.Add(String.Format("{0,-36} {1}",safe,address));
            }
        }
        var output=new string[lines.Count]; lines.CopyTo(output); return output;
    }
}
'@
}
Write-Host '@@SEARCH@@'
try {
    $bridges = @([Hue2LoxLocalDiscovery]::Find())
    Write-Host "`nBRIDGE                               IPv4"
    if ($bridges.Count) { $bridges | ForEach-Object { Write-Host $_ } }
    else { Write-Host '@@NONE@@' }
} catch { Write-Error ('@@FAILED@@ ' + $_.Exception.Message) }
}
