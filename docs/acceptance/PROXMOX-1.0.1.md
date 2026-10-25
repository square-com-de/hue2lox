# Proxmox Linux VM acceptance — scope

The consolidated [independent Deployer report](../CONTAINER-ACCEPTANCE-1.0.1.md) records the tested system, immutable image/file identities, executed commands and results. It supersedes this path’s earlier partial status.

The HTTP quick start passed real browser login, reload, changed-password login after restart, cold restore into another volume and retained-password browser login. The unchanged file was obtained from PR49 commit `bd8b4d172cafd8db9e602c992ec3e9704a4ce420`; the same bytes are included in PR50.

A coordinated VM reboot on 25 October 2026 also passed: both instances automatically became healthy, retained passwords worked, state hashes matched the pre-reboot backup and HTTP browser login succeeded.

The OS was reused for this final quick-start check; the application and data volume were fresh. This is not a second clean-OS test. Portainer UI, deliberately disabled control flags in recovery, real bridge discovery/pairing and Loxone commands are not covered. The separate self-signed HTTPS browser profile remains unaccepted; no warning was bypassed. The isolated VM’s firewall exception is not an end-user step.

These results do not open the future stable gate or authorize a blanket hardware/support claim.
