CREATE USER admin_inv WITH PASSWORD 'inventario';

CREATE DATABASE inv_db WITH 
    OWNER admin_inv
    ENCODING 'UTF8'
    LC_COLLATE 'en_US.UTF-8'
    LC_CTYPE 'en_US.UTF-8'
    TEMPLATE template0;

GRANT ALL PRIVILEGES ON DATABASE inv_db TO admin_inv;


from apps.accounts.models import CustomUser
u = CustomUser.objects.create_user(
    username="cliente2",
    password="cliente1234",
    rol=CustomUser.CLIENTE
)
u.save()
exit()