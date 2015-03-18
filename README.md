# http-proxy
Working HTTP Proxy in **Python/Twisted** with HTTP basic auth and users stored in **MySQL** table.<br />
Files:<br />
twisted-proxy.py: the server itself, can be invoked with "-h" flag.<br />
proxy-client.py: HTTP Proxy client with HTTP Basic Auth<br />
manage-users.py: script that allows adding, deleting and modifying users.<br />
server.conf: server configuration file.<br />
SQL/initial-data.sql: MySQL schema for storing user accounts.<br />
