## Security Incident Report - Wed Feb 19 07:44:28 PM PST 2025
### Key Details
### System Impact
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda2       480G  439G   17G  97% /
### Network Connections
tcp        0      0 127.0.0.1:38235         0.0.0.0:*               LISTEN      2149/ivpn-service   
tcp        0      0 127.0.0.1:5432          0.0.0.0:*               LISTEN      2309/postgres       
tcp        0      0 0.0.0.0:5000            0.0.0.0:*               LISTEN      2815/shairport-sync 
tcp        0      0 0.0.0.0:6379            0.0.0.0:*               LISTEN      2141/redis-server 0 
tcp        0      0 0.0.0.0:8080            0.0.0.0:*               LISTEN      2165/tinyproxy      
tcp        0      0 0.0.0.0:8765            0.0.0.0:*               LISTEN      2124/python3        
tcp        0      0 0.0.0.0:9000            0.0.0.0:*               LISTEN      2154/moauthd        
tcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN      2243/nginx: master  
tcp        0      0 127.0.0.1:40975         0.0.0.0:*               LISTEN      2177/containerd     
tcp        0      0 0.0.0.0:1880            0.0.0.0:*               LISTEN      2611/node-red       
tcp        0      0 127.0.0.1:33060         0.0.0.0:*               LISTEN      2318/mysqld         
tcp        0      0 127.0.0.1:631           0.0.0.0:*               LISTEN      2120/cupsd          
tcp        0      0 127.0.0.1:9040          0.0.0.0:*               LISTEN      2303/tor            
tcp        0      0 127.0.0.1:9050          0.0.0.0:*               LISTEN      2303/tor            
tcp        0      0 127.0.0.1:3306          0.0.0.0:*               LISTEN      2318/mysqld         
tcp        0      0 0.0.0.0:43253           0.0.0.0:*               LISTEN      372637/python       
tcp6       0      0 :::5000                 :::*                    LISTEN      2815/shairport-sync 
tcp6       0      0 ::1:631                 :::*                    LISTEN      2120/cupsd          
tcp6       0      0 :::8080                 :::*                    LISTEN      2165/tinyproxy      
tcp6       0      0 :::9000                 :::*                    LISTEN      2154/moauthd        
tcp6       0      0 :::80                   :::*                    LISTEN      2243/nginx: master  
tcp6       0      0 :::1716                 :::*                    LISTEN      290518/kdeconnectd  
tcp6       0      0 :::43253                :::*                    LISTEN      372637/python       
