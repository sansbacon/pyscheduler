FROM ubuntu:18.04

RUN apt-get update
RUN apt-get -y install --no-install-recommends python3 python3-pip coinor-cbc

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True
ENV SHEETFU_CONFIG_TYPE=service_account
ENV SHEETFU_CONFIG_PROJECT_ID=pickleball-315623
ENV SHEETFU_CONFIG_PRIVATE_KEY_ID=72469838c4d6600f96f8e437de7b3e1f5558df2d
ENV SHEETFU_CONFIG_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCtBZk/EZ9pMOuc\nX2tggjmBQJcB+aucT6Klf5yWdVVUNhDsqYPuBAKUKk1hwaDmmy5uJwJEqToMRhIZ\nhxKmD4GUB+Y4Lj04TX+ILPEUEbEwn+VRKT7HO+s4RLQeL0CgwQtb02YSLzPX+F/1\nZdvqQQaNA2M8oxEPFmzvVa8uOljVA7pRWAPh2dGqBvyWMoYS8bAQh4EJuozYgnbf\nCrWzIOX4jff9NiOKjMRupO4NuiSwRSMBCn3FRZYUhKh/p26q/iYXWE+6QYP7BeSZ\n01BkkU/LN7UVNE+X11jQ9TlwUThRIZx6FT+jsjGDeKcKdj5QzwzoLjb+tpDIwljm\ni+9f+eEFAgMBAAECggEAJQ8qLgtTAueuy5FXkTYLZZ8lSQ/GXWZkPsEI0+RBWNZ0\nxRAg+TnkKIKwDOR5l3M9HGxgDL9XdtoKVevrx2RSW5fejIGA7N6SlqMTpvoMIw9Y\ngYwNTYTMwsJadw2lcNkwWuR6fCIen19shEYjNrdjVRBY8Nu3k2z4+8F1Ung+Xy+B\nNdSa8+RmyIPnD+Zo1ODMCmpKCtgvYBIXYVarCOuPGATgN8EabZI4jUs8RPLfmiRs\nlwm9WK4z40bTPDzx/3ttUmDAVu/5XTi0wWso2bdhsOtHP0xLlW8fkc7TW0nfkq2j\nWtdc5+mDnSSBs44AM2r8D2H6FzOdc4ju0I6SPDloIQKBgQDcxilJirf28g8GWA3D\n+ZmJnhLTadnGnnDhPq2rHbE8qe8n84CwAk0XtUEivG1Ckzkam6DadxYAHIdNwGnF\nt7vjfaKAJ3fwPTed2J5gSOppMWLovL3DOyLJ0F+bb2affi1v6iISVdXTBsRfrJdV\nE/AlpfZK+uyB39PkbnMWPhjF5QKBgQDIoO3fDByVzm3KfHg+a9aCDsiURbtkqGLV\nAambobHFWr+nTFigD0iFpWte4Dol7sddlAQulZQ7JwYohB8olHjvLGP9gmnvj+bH\nScS3C83dwUPh6gk+7798t1iGMDOELuNghBB9HmZllBraJch72kNuhGe0MABpUWoY\nw3uJt7j8oQKBgBma/hTiet2wS1/P/KC7JTyZ0dMlVrW7kJn/PAM5qWHAz9URX96K\nFcjnI8vUkNOE4b2dSTWtVCblKCgzZdEhsy/6VUuJyFZbs0SiaBQAwPc8XB1kLpoj\nFLDVcxFDBWMALmLpg9QeknMsOMBj8xVR/6tOKVee7KlPfXLkAIMW5qalAoGAZ8KD\nA0YaSofWVFCHR5EyAVVv+u8NeYN0icEwXKMFc5H5aKaddzowQZ5Jp2nD6PZS+Vyh\nxQ3q+aS3FKEwFCalXNzSYbve2dzMd+j46cobEELxvpbxbTFFEVUpXUz0d7pgMfxb\nIrpkLsioEoZT52n8Ud38XD4vGEjY3DHNZG42J8ECgYBHoK2eRYtfHf2VKMZgF7TP\nbgc/vcHHGxTkx5ctPy9yVlNH7dBH1dUmIg1Gf5dQrntC29YFSgYCutwbUu7v3Ijx\nYgPRDwi229SF5KElK2FyAoIfehdrWoN/jXAA3sRPRkV1qHGEp4szxGajWOq13pBh\nOVLi4Hi0gCZQZWsMzQ8uYA==\n-----END PRIVATE KEY-----\n"
ENV SHEETFU_CONFIG_CLIENT_EMAIL pickleballservice@pickleball-315623.iam.gserviceaccount.com
ENV SHEETFU_CONFIG_CLIENT_ID 105630674946243670955
ENV SHEETFU_CONFIG_AUTH_URI https://accounts.google.com/o/oauth2/auth
ENV SHEETFU_CONFIG_TOKEN_URI https://oauth2.googleapis.com/token
ENV SHEETFU_CONFIG_AUTH_PROVIDER_URL https://www.googleapis.com/oauth2/v1/certs
ENV SHEETFU_CONFIG_CLIENT_CERT_URL https://www.googleapis.com/robot/v1/metadata/x509/pickleballservice%40pickleball-315623.iam.gserviceaccount.com

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Install production dependencies.
RUN python3 -m pip install Flask gunicorn pandas pulp sheetfu

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
