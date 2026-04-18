CREATE USER admin_inv WITH PASSWORD 'inventario';

CREATE DATABASE invpro_db WITH 
    OWNER admin_inv
    ENCODING 'UTF8'
    LC_COLLATE 'en_US.UTF-8'
    LC_CTYPE 'en_US.UTF-8'
    TEMPLATE template0;

GRANT ALL PRIVILEGES ON DATABASE invpro_db TO admin_inv;
