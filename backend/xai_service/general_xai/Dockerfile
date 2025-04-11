FROM python:3.8-slim-buster

WORKDIR /xai
COPY  . .



#RUN python -m pip install -r requirements.txt

#EXPOSE 5003
#CMD flask --app "/xai_service/pytorch_cam:create_app(cam_method='${CAM_METHOD}')" run --host=0.0.0.0 -p 5003
ENTRYPOINT ["tail", "-f", "/dev/null"]