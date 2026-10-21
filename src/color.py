"""sRGB/Hue conversion using per-light capabilities and explicit fallbacks."""
import math

# Compatibility fallback (Hue gamut C), only when device data is unavailable.
GAMUT = ((0.6915, 0.3083), (0.17, 0.7), (0.1532, 0.0475))



def light_parameters(resource):
    """Keep only validated conversion data; never retain keys or other metadata."""
    result = {}
    color = resource.get('color')
    gamut = color.get('gamut') if type(color) is dict else None
    if type(gamut) is dict:
        try:
            points = tuple((gamut[name]['x'], gamut[name]['y']) for name in ('red', 'green', 'blue'))
            valid = all(type(v) in (int, float) and math.isfinite(v) and 0 <= v <= 1
                        for point in points for v in point)
            a, b, c = points
            area = (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0]) if valid else 0
            if valid and all(x+y <= 1.000001 for x,y in points) and abs(area) > 1e-9:
                result['color'] = {'gamut': {name:dict(x=point[0], y=point[1])
                                           for name, point in zip(('red','green','blue'), points)}}
        except (KeyError, TypeError):
            pass
    temperature = resource.get('color_temperature')
    schema = temperature.get('mirek_schema') if type(temperature) is dict else None
    if type(schema) is dict:
        low, high = schema.get('mirek_minimum'), schema.get('mirek_maximum')
        if type(low) is int and type(high) is int and 1 <= low <= high <= 1000:
            result['color_temperature'] = {'mirek_schema': {'mirek_minimum':low, 'mirek_maximum':high}}
    return result


def gamut_for(resource):
    gamut = light_parameters(resource or {}).get('color', {}).get('gamut')
    return tuple((gamut[name]['x'], gamut[name]['y']) for name in ('red','green','blue')) if gamut else GAMUT


def rgb_values(rgb):
    if type(rgb) is not dict or set(rgb) != {'r', 'g', 'b'}:
        raise ValueError('rgb requires exactly r, g, b')
    values = tuple(rgb[c] for c in ('r', 'g', 'b'))
    if any(type(v) not in (int, float) or not math.isfinite(v) or not 0 <= v <= 255 for v in values):
        raise ValueError('RGB channels must be finite numbers from 0 to 255')
    return values


def clip_xy(point, gamut=GAMUT):
    a,b,c=gamut
    cross=lambda u,v: u[0]*v[1]-u[1]*v[0]
    sub=lambda u,v: (u[0]-v[0],u[1]-v[1])
    signs=[cross(sub(v,u),sub(point,u)) for u,v in ((a,b),(b,c),(c,a))]
    if min(signs)>=-1e-12 or max(signs)<=1e-12:
        return point
    candidates=[]
    for u,v in ((a,b),(b,c),(c,a)):
        dx,dy=sub(v,u)
        t=max(0,min(1,((point[0]-u[0])*dx+(point[1]-u[1])*dy)/(dx*dx+dy*dy)))
        candidates.append((u[0]+t*dx,u[1]+t*dy))
    return min(candidates,key=lambda q:(q[0]-point[0])**2+(q[1]-point[1])**2)


def rgb_xy(rgb, light=None):
    """Color only; brightness remains a separate, explicit percentage."""
    values=rgb_values(rgb)
    if not any(values):
        return None
    def linear(v):
        v=v/255
        return ((v+0.055)/1.055)**2.4 if v>0.04045 else v/12.92
    r,g,b=map(linear,values)
    # Hue developer wide RGB D65 conversion matrix.
    x=r*0.664511+g*0.154324+b*0.162028
    y=r*0.283881+g*0.668433+b*0.047685
    z=r*0.000088+g*0.072310+b*0.986039
    total=x+y+z
    return clip_xy((x/total,y/total), gamut_for(light))


def loxone_rgb(value):
    """Classic RGB packed percent value R + G*1000 + B*1000000."""
    if type(value) not in (int,float) or not math.isfinite(value) or value != int(value) or not 0 <= value <= 100100100:
        raise ValueError('invalid classic Loxone RGB value')
    value=int(value)
    r=value%1000;g=(value//1000)%1000;b=value//1000000
    if max(r,g,b)>100:
        raise ValueError('RGB percent channels must be from 0 to 100')
    peak=max(r,g,b)
    if not peak:
        return {'rgb': {'r':0,'g':0,'b':0}}
    # Preserve Hue's separate dimming semantics: scale chromaticity channels
    # to their relative ratio and take maximum Loxone channel as brightness.
    return {'rgb': dict(zip(('r','g','b'),(v*255/peak for v in (r,g,b)))), 'brightness':peak}


def kelvin_mirek(value, light=None):
    """Convert absolute Kelvin, clamping to the lamp's actual mirek range."""
    if type(value) not in (int,float) or not math.isfinite(value) or not 1000 <= value <= 20000:
        raise ValueError('kelvin must be a finite number from 1000 to 20000')
    schema = light_parameters(light or {}).get('color_temperature', {}).get('mirek_schema', {})
    low, high = schema.get('mirek_minimum',153), schema.get('mirek_maximum',500)
    return max(low,min(high,math.floor(1000000/value+0.5)))


def loxone_lumitech(value):
    """RGB or 200000000 + brightnessPercent*10000 + kelvin."""
    if type(value) not in (int,float) or not math.isfinite(value) or value != int(value):
        raise ValueError('Lumitech requires a finite integer')
    value=int(value)
    if value < 200000000:
        return loxone_rgb(value)
    brightness,kelvin=divmod(value-200000000,10000)
    if not 0 <= brightness <= 100:
        raise ValueError('invalid Lumitech brightness')
    kelvin_mirek(kelvin)
    if brightness==0:
        return {'on':False}
    return {'kelvin':kelvin,'brightness':brightness}
