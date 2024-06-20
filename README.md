# Khayyal Backend
## Notes on Deployment
For cloud related services we rely on `GCP (Google Cloud Platform)`.
The application gets deployed in an instance of `GCE(Google Compute Engine)`. Right now
only the `dev` server is live. The `swagger docs` are accessible on `http://34.45.27.123:8000/docs/`.
Access the [dev server](http://34.45.27.123:8000/docs/).
### Dev
With each pushes to the `main` branch the application gets automatically deployed
to the `server` using `Github Actions CI/CD Workflow`. The workflow script is located in 
the `.github/workflows` directory with the filename
[deploy-to-khayyal-dev.yml](.github/workflows/deploy-to-khayyal-dev.yml). 

To understand the steps the workflow executes in order to completion the 
deployment please see # Issue [#26]. 

When each of your PRs get merged into main the workflow automatically executes. 
After the execution of the workflow (typically a few minutes post merge) please
check whether the deployment has been successful by trying to access the docs from
the web. 

If it is accessible then all is okay. You can verify whether the new
functionalities implemented by you are working expectedly from the docs.

In case it is not accessible and the browser is throwing some kind of error then
the deployment has not been successful. 

To mitigate the issue, `ssh` into the dev server and try to run the `khayyal-backend`
docker image without the `-d` flag to not start it in a detached mood. 

Run the following commands:

```bash
sudo docker stop khayyal-backend # to stop the container if already running
sudo docker rm khayyal-backend # remove the container
```

After running the commands try to start the docker container
using the following command:

```bash
sudo docker run -p 8000:80 --name khayyal-backend --mount type=bind,source=/home/khayyal-backend/secrets.json,target=/app/secrets.json --mount type=bind,source=/home/khayyal-backend/logs,target=/app/logs khayyal-backend
```

The absense of the `-d` flag from the `docker run` command will run the container
in the current terminal session. You would be able to see what is going wrong in the
start-up process of the application. 

A very common issue that results in deployment failure is absense of keys in the `secrets.json`
file. For example if you've added new `keys` there during development of a new feature
and haven't updated the keys in the `server` when the application would not be
able to find the `keys` and exit with error. 

The best way to handle this is by adding the new `keys` and the corresponding values
in the `server` prior to raising the PR. However, if you have forgotten to add the and
successfully identified that the missing keys are the root of the problem, do not freak out!

Add the keys and the values in the `server` first. After adding the keys, re-run
the corresponding `github action` from the `actions` tab in `github`. 

Never forget to ask for help if you are stuck! Happy coding :)



