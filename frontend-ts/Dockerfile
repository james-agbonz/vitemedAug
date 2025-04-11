FROM node:22.9.0

WORKDIR /app

COPY . /app

EXPOSE 5173

RUN yarn

# ENTRYPOINT [ "tail" , "-f" , "/dev/null" ]
ENTRYPOINT [ "yarn", "dev" ]