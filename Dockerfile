# 베이스 이미지로 Node.js 사용
FROM node:16.20.2

# step 2 : Package Install
RUN apt -y update && apt -y upgrade && apt -y install git net-tools vim mysql-client

# 작업 디렉토리 설정
WORKDIR '/root'

# 의존성 설치
RUN git clone https://github.com/wjdguswn1203/PaperTechTrend ptt1
WORKDIR '/root/ptt1/server'
RUN npm install
RUN npm install -g nodemon

# 다른 git 가져오기
WORKDIR '/root'
RUN git clone https://github.com/raminicano/PaperTechTrend ptt2
WORKDIR '/root/ptt2'
RUN npm install
RUN npm install -g nodemon

# 애플리케이션이 실행될 포트 설정
EXPOSE 8000 8500

# 애플리케이션 시작 명령어
CMD nodemon /root/ptt1/server/app.js & nodemon /root/ptt2/app.js
