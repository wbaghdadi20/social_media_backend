# Social Media Backend

## Project Overview

This is a backend application for a social media platform built with FastAPI. The project utilizes PostgreSQL for data storage and Nginx as a load balancer to distribute requests between multiple FastAPI app instances. The infrastructure is containerized using Docker, allowing for easy deployment and scalability.

The backend includes features such as user authentication, post creation, commenting, liking posts/comments, and following other users. All interactions with the application are secured through JWT-based authentication.

### CI/CD Pipeline

The project uses a Continuous Integration and Continuous Deployment (CI/CD) pipeline set up with GitHub Actions. Whenever code is pushed to the repository, the pipeline is triggered on an EC2 runner, which performs the following actions:

1. **Code Testing**: Runs unit tests using Dockerized test containers to ensure the functionality and stability of the code.
2. **Building and Tagging**: Builds Docker images for testing and production, tagging them appropriately.
3. **Container Deployment**: Deploys the updated application containers on the EC2 instance, replacing old containers with new ones for the production environment.

### Deployment on EC2 Instance

The project is hosted on an EC2 instance with Docker. The EC2 instance runs the following containers:

1. `postgres`: PostgreSQL database container for persistent data storage.
2. `app_instance_1` and `app_instance_2`: Two FastAPI application instances for redundancy and load balancing.
3. `load_balancer`: Nginx container serving as the load balancer to distribute traffic between the application instances.

You can access the live application on the following link: [Social Media Backend Instance](http://54.176.191.192/docs)

---

## Environment Variables Setup

To ensure the security and flexibility of the application, several environment variables are required. These variables store sensitive information such as database credentials and secret keys. Instead of hardcoding these values, you will be prompted to input them during the setup process.

### List of Environment Variables

| Variable Name       | Description                                                                | Generation/Recommendation                                                                                                  |
| ------------------- | -------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `POSTGRES_USER`     | Username for the PostgreSQL database.                                      | **Create your own.** Choose a strong username for database access.                                                         |
| `POSTGRES_PASSWORD` | Password for the PostgreSQL database user.                                 | **Create your own.** Use a strong, secure password.                                                                        |
| `POSTGRES_DB`       | Name of the PostgreSQL database.                                           | **Create your own.** Choose a meaningful name for your database.                                                           |
| `SECRET_KEY`        | Secret key used for JWT authentication and other cryptographic operations. | **Generate your own.** Use a secure random string. You can generate one by running `openssl rand -hex 32` in your terminal |

---

## How to Run the Project Locally

You can run this project on your local machine using Docker. Follow the instructions below based on your operating system.

### Environment Variables Input

Before running the setup scripts, ensure you have the necessary environment variables ready. You will need to modify the setup script and add your environment variables:

- `POSTGRES_USER`: Your PostgreSQL username.
- `POSTGRES_PASSWORD`: Your PostgreSQL password.
- `POSTGRES_DB`: Your PostgreSQL database name.
- `SECRET_KEY`: A secure secret key for JWT and other cryptographic operations.

**Note:** The `ALGORITHM` and `ACCESS_TOKEN_EXPIRE_MINUTES` do not require change.

### Windows

1. Open PowerShell and copy the script below into a `.ps1` file (e.g., `setup.ps1`):

   ```powershell
   # Clean up Docker images, containers, and networks
   Write-Host "Cleaning up Docker images, containers, and networks..."
   docker rm -f app_instance_1 app_instance_2 load_balancer postgres test_postgres
   docker rmi -f app # Remove only the 'app' image, if it exists
   docker network prune --force

   # Create Docker networks
   Write-Host "Creating Docker networks..."
   docker network create app_network
   docker network create test_app_network

   # Pull the latest PostgreSQL image
   Write-Host "Pulling latest PostgreSQL image..."
   docker pull postgres:latest

   # Run the Test-PostgreSQL Docker container
   Write-Host "Running Test-PostgreSQL Docker container..."
   docker run -d `
   --name test_postgres `
   --network test_app_network `
   -p 2345:5432 `
   -e POSTGRES_USER=test_user `
   -e POSTGRES_PASSWORD=test_password `
   -e POSTGRES_DB=test_db `
   -v pg_test_data:/var/lib/postgresql/data `
   postgres:latest

   # Build the FastAPI Test image
   Write-Host "Building FastAPI Test image..."
   docker build --target test . -t test_app

   # Run tests inside the test container
   Write-Host "Running tests..."
   docker run --rm `
   --network test_app_network `
   test_app

   # Clean up test container images
   Write-Host "Cleaning up test container images..."
   docker rmi test_app

   # Build the FastAPI production image
   Write-Host "Building FastAPI production image..."
   docker build --target prod . -t app

   # Run the Production PostgreSQL Docker container
   Write-Host "Running Production PostgreSQL container..."
   docker run -d `
   --name postgres `
   --network app_network `
   -p 5432:5432 `
   -e POSTGRES_USER=$POSTGRES_USER `
   -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD `
   -e POSTGRES_DB=$POSTGRES_DB `
   -v pg_prod_data:/var/lib/postgresql/data `
   postgres:latest

   # Run the FastAPI production app containers
   Write-Host "Running FastAPI production app containers..."
   docker run -d `
   --name app_instance_1 `
   --network app_network `
   -e SECRET_KEY=$SECRET_KEY `
   -e ALGORITHM=HS256 `
   -e ACCESS_TOKEN_EXPIRE_MINUTES=30 `
   -e SQLALCHEMY_DATABASE_URL=postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@postgres:5432/$POSTGRES_DB `
   app

   docker run -d `
   --name app_instance_2 `
   --network app_network `
   -e SECRET_KEY=$SECRET_KEY `
   -e ALGORITHM=HS256 `
   -e ACCESS_TOKEN_EXPIRE_MINUTES=30 `
   -e SQLALCHEMY_DATABASE_URL=postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@postgres:5432/$POSTGRES_DB `
   app

   # Build the Nginx Docker image (optional if it doesn't change)
   Write-Host "Building Nginx Docker image..."
   docker build -f Dockerfile.nginx . -t nginx

   # Run the Nginx load balancer container
   Write-Host "Running Nginx load balancer container..."
   docker run -d `
   --name load_balancer `
   --network app_network `
   -p 80:80 `
   nginx

   Write-Host "Local testing and setup completed."
   ```

2. Run the script in PowerShell using the following command:

   ```powershell
   ./setup.ps1
   ```

### Linux / macOS

1. Open your terminal and copy the script below into a `.sh` file (e.g., `setup.sh`):

   ```bash
   # Clean up Docker images, containers, and networks
   echo "Cleaning up Docker images, containers, and networks..."
   docker rm -f app_instance_1 app_instance_2 load_balancer postgres test_postgres
   docker rmi -f app # Remove only the 'app' image, if it exists
   docker network prune --force

   # Create Docker networks
   echo "Creating Docker networks..."
   docker network create app_network
   docker network create test_app_network

   # Pull the latest PostgreSQL image
   echo "Pulling latest PostgreSQL image..."
   docker pull postgres:latest

   # Run the Test-PostgreSQL Docker container
   echo "Running Test-PostgreSQL Docker container..."
   docker run -d \
   --name test_postgres \
   --network test_app_network \
   -p 2345:5432 \
   -e POSTGRES_USER=test_user \
   -e POSTGRES_PASSWORD=test_password \
   -e POSTGRES_DB=test_db \
   -v pg_test_data:/var/lib/postgresql/data \
   postgres:latest

   # Build the FastAPI Test image
   echo "Building FastAPI Test image..."
   docker build --target test . -t test_app

   # Run tests inside the test container
   echo "Running tests..."
   docker run --rm \
   --network test_app_network \
   test_app

   # Clean up test container images
   echo "Cleaning up test container images..."
   docker rmi test_app

   # Build the FastAPI production image
   echo "Building FastAPI production image..."
   docker build --target prod . -t app

   # Run the Production PostgreSQL Docker container
   echo "Running Production PostgreSQL container..."
   docker run -d \
   --name postgres \
   --network app_network \
   -p 5432:5432 \
   -e POSTGRES_USER=$POSTGRES_USER \
   -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
   -e POSTGRES_DB=$POSTGRES_DB \
   -v pg_prod_data:/var/lib/postgresql/data \
   postgres:latest

   # Run the FastAPI production app containers
   echo "Running FastAPI production app containers..."
   docker run -d \
   --name app_instance_1 \
   --network app_network \
   -e SECRET_KEY=$SECRET_KEY \
   -e ALGORITHM=HS256 \
   -e ACCESS_TOKEN_EXPIRE_MINUTES=30 \
   -e SQLALCHEMY_DATABASE_URL=postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@postgres:5432/$POSTGRES_DB \
   app

   docker run -d \
   --name app_instance_2 \
   --network app_network \
   -e SECRET_KEY=$SECRET_KEY \
   -e ALGORITHM=HS256 \
   -e ACCESS_TOKEN_EXPIRE_MINUTES=30 \
   -e SQLALCHEMY_DATABASE_URL=postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@postgres:5432/$POSTGRES_DB \
   app

   # Build the Nginx Docker image (optional if it doesn't change)
   echo "Building Nginx Docker image..."
   docker build -f Dockerfile.nginx . -t nginx

   # Run the Nginx load balancer container
   echo "Running Nginx load balancer container..."
   docker run -d \
   --name load_balancer \
   --network app_network \
   -p 80:80 \
   nginx

   echo "Local testing and setup completed."
   ```

2. Make the script executable by running the command:

   ```bash
   chmod +x setup.sh
   ```

3. Run the script using the command:

   ```bash
   ./setup.sh
   ```

---

## Troubleshooting

- **Port Conflicts**: If ports `5432`, `2345`, or `80` are already in use on your machine, you may encounter errors. Ensure these ports are free or modify the scripts to use different ports.

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.
