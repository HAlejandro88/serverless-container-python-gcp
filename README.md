
`python -m venv env or python3 -m venv env` to create a virtual enviroment then run 
`source env/bin/activate`

or if it is easier for you to run it with Docker you need to run the next command
`docker run `
`docker tag serverless-py-amd64 us-central1-docker.pkg.dev/<project-id>/<arifact-repo-name>/<name-image>:<version>`

to automate this project with github actions youneed to follow the next steps
- create this path in your root folder teh next path **github/workflows/main.yml**  or run his command`mkdir .github/workflows/main.yml`
- copy the next code 
```yaml
name: Test, Build, and Push to Google Cloud run

on: 
  workflow_dispatch:
  push:
    branches:
      - "main"
      - "18-end"
      - "19-start"
      - "19-end"
      - "20-start"
      - "20-end"
      - "master"


jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.8"
      - name: Install requirements
        run: |
          python -m pip install -r src/requirements.txt
          python -m pip install pytest
      - name: Run tests
        env:
          MODE: "github actions"
        run: |
          pytest src/tests.py
  build_deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      - name: Set up QEMU
        uses: docker/setup-qemu-action@v2
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      - id: 'auth'
        name: 'Authenticate to Google Cloud'
        uses: 'google-github-actions/auth@v1'
        with:
          credentials_json: '${{ secrets.GOOGLE_CREDENTIALS }}'
      - name: Build container image
        run: |
            docker build -f Dockerfile -t inline-docker-tag .
            docker tag inline-docker-tag ${{ secrets.CONTAINER_IMAGE_URL }}:latest
            docker tag inline-docker-tag ${{ secrets.CONTAINER_IMAGE_URL }}:${GITHUB_RUN_ID}
            gcloud auth configure-docker ${{ secrets.GCLOUD_REGION }}-docker.pkg.dev
            docker push ${{ secrets.CONTAINER_IMAGE_URL }} --all-tags
      - name: Deploy container to Cloud Run
        run: |
            gcloud run deploy serverless-py-run \
              --image=${{ secrets.CONTAINER_IMAGE_URL }}:${GITHUB_RUN_ID} \
              --allow-unauthenticated \
              --region=${{ secrets.GCLOUD_REGION }} \
              --project=${{ secrets.GCLOUD_PROJECT_ID }}
```

Obtener el project number```gcloud projects describe PROJECT_ID --format="value(projectNumber)"```
Crear permisos para secrets manager en GCP 
```bash
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:PROJECT_NUMBER@cloudbuild.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```


to run secrets in your local machine 
`gcloud auth application-default login`


add another workflow to create an update secrets in Secrets manager 
Steps
- create new file in github workflows name secrets.yaml
- copy and paste the nex code 

```yml
name: Google Cloud Secrets Manager Workflow

on: 
  workflow_dispatch:

jobs:
  update_secret:
    runs-on: ubuntu-latest
    steps:
      - id: 'auth'
        name: 'Authenticate to Google Cloud'
        uses: 'google-github-actions/auth@v1'
        with:
          credentials_json: '${{ secrets.GOOGLE_CREDENTIALS }}'
      - name: Configure dotenv file
        run: |
          cat << EOF > .env
          MODE=${{ secrets.APP_MODE }}
          TOKEN=${{ secrets.APP_TOKEN }}
          EOF
      - name: Run a new version of secrets
        run: |
          gcloud secrets versions add ${{ secrets.GCLOUD_SECRET_LABEL }} --data-file .env
      # add or remove permitions in secrets manager to manage cloud run
      # - name: Run a new version of secrets
      #   run: |
      #     gcloud secrets remove-iam-policy-binding ${{ secrets.GCLOUD_SECRET_LABEL }} --member='serviceAccount:' --role='roles/secretmanager.secretAccessor'
```
- add secres value en in github (navigate into configuratiosn secrets-variables actions and create all teh variables )