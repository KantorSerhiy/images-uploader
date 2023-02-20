# Images-uploader setup

Test task for HEXOCEAN

### Clone project
````
git clone https://github.com/KantorSerhiy/images-uploader.git
````

### Docker should be installed on your machine.
#### How to run:
- copy .env-sample -> .env and populate with all required data
- `docker-compose up --build`


Go to the container and create superuser:
````
docker exec -it <container_id> bash
python manage.py createsuperuser
````

You can go to create new user or custom tier in admin panel.

## Endpoints:

Get list of images:
````
http://127.0.0.1:8000/api/image/
````
Upload images:
````
http://127.0.0.1:8000/api/image/
````
Create binary link:
````
http://127.0.0.1:8000/api/image/<image_id>/binary-image/
````
