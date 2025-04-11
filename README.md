### 1. Start Services by Docker Compose

TBD

### 2. Start Services Locally

Make sure you have the following variables in the environment (or the `.env.dev` file):

```properties
ENV=dev
MONGO_CONF_STR=<mongodb connection string>
MONGO_DB_NAME=<the name of the database>
```

#### 2.1 Launch the services

**Central**

```bash
flask --app backend/central/main.py run --host=0.0.0.0 --port=5006
```

**Database service**

For instance, the hyperk dataset:

```bash
flask --app backend/dataset_service/hyper_kvasir run --host=0.0.0.0 -p 5002
```

**Model service**

```bash
flask --app backend/model_service/effnetv2s run --host=0.0.0.0 -p 5001
```

**Model eval service**

```bash
flask --app backend/evaluation_service/model_eval run --host=0.0.0.0 -p 5005
```

#### 2.2 Register the services
