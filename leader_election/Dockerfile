# Use an official Python image as the base image
FROM python:3.9-slim

# Install necessary packages
RUN pip install pyzmq

# Set the working directory
WORKDIR /home/nelli/vscode_prjs/projeto-2-mc714/leader_election

# Copy the source code into the container
COPY . .

# Set the entry point to Python
ENTRYPOINT ["python"]
