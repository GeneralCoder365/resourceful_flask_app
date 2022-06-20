FROM tiangolo/uwsgi-nginx-flask:python3.8

# sets default shell for all commands to /bin/bash instead of /bin/sh
# SHELL ["/bin/bash", "-c"]

RUN apt update

RUN mkdir /code
WORKDIR /code

# 0. Install essential packages
ADD requirements.txt /code/
RUN pip install -r requirements.txt --no-cache-dir
ADD . /code/

# 0.5: Apply django migrations
# RUN python manage.py migrate

# 0. Install essential packages
# RUN apt-get update \
#     && apt-get install -y \
#         build-essential \
#         cmake \
#         git \
#         wget \
#         unzip \
#         unixodbc-dev \
#     && rm -rf /var/lib/apt/lists/*

# 1. Install Chrome (root image is debian)
# See https://stackoverflow.com/questions/49132615/installing-chrome-in-docker-file
ARG CHROME_VERSION="google-chrome-stable"
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
  && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
  && apt-get update -qqy \
  && apt-get -qqy install \
    ${CHROME_VERSION:-google-chrome-stable} \
  && rm /etc/apt/sources.list.d/google-chrome.list \
  && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

# 2. Install Chrome driver used by Selenium
# http://chromedriver.storage.googleapis.com/$LATEST/chromedriver_linux64.zip
# LATEST=$(wget --no-verbose --output-document - http://chromedriver.storage.googleapis.com/LATEST_RELEASE)
# ! -c is cpu shares weight
# ! doing /bin/bash because shell is /bin/sh, but source expects /bin/bash, perhaps because it puts its initialization in ~/.bashrc
# ! this causes /bin/sh: 1: MY_COMMAND: not found
# /bin/bash -c "wget -q -O - http://chromedriver.storage.googleapis.com/$LATEST/chromedriver_linux64.zip | unzip -d /usr/local/bin -o"
# LATEST=$()
RUN /bin/bash -c 'LATEST=$`wget -q -O - https://chromedriver.storage.googleapis.com/LATEST_RELEASE`'
#  \
#   && wget -q -O - https://chromedriver.storage.googleapis.com/$LATEST/chromedriver_linux64.zip 
  # | unzip -d /usr/local/bin -o \
  # && chmod +x /usr/local/bin/chromedriver
# && \  
# 102.0.5005.61
# ${LATEST}
# /bin/bash -c `wget http://chromedriver.storage.googleapis.com/102.0.5005.61/chromedriver_linux64.zip`
RUN wget http://chromedriver.storage.googleapis.com/102.0.5005.61/chromedriver_linux64.zip
# && \  
RUN unzip chromedriver_linux64.zip && ln -s $PWD/chromedriver /usr/local/bin/chromedriver
# RUN /bin/bash -c 'wget -q -O - http://chromedriver.storage.googleapis.com/${LATEST}/chromedriver_linux64.zip'
# | unzip -d /usr/local/bin/chromedriver -o`

ENV PATH="/usr/local/bin/chromedriver:${PATH}"

# 3. Install selenium in Python
RUN pip install -U selenium

# 4. Finally, copy python code to image
COPY . /home/site/wwwroot

# 6: Set Up ssh server
ENV SSH_PASSWD "root:Docker!"
RUN apt-get update \
        && apt-get install -y --no-install-recommends dialog \
        && apt-get update \
	&& apt-get install -y --no-install-recommends openssh-server \
	&& echo "$SSH_PASSWD" | chpasswd 


# 7: Copy config files
COPY sshd_config /etc/ssh/
COPY init.sh /usr/local/bin/


# # 5. Install other packages in requirements.txt
# RUN cd /home/site/wwwroot && \
#     pip install -r requirements.txt

# ssh
# ENV SSH_PASSWD "root:Docker!"
# RUN apt-get update \
#         && apt-get install -y --no-install-recommends dialog \
#         && apt-get update \
#         && apt-get install -y \
#         build-essential \
#         cmake \
#         git \
#         wget \
#         unzip \
#         unixodbc-dev \
#     && rm -rf /var/lib/apt/lists/* \
# && apt-get install -y --no-install-recommends openssh-server \
    # ! OpenSSH is a connectivity tool for remote login that uses the SSH protocol so shouldn't need to be installed
#  && echo "$SSH_PASSWD" | chpasswd 

# COPY sshd_config /etc/ssh/
# COPY init.sh /usr/local/bin/

RUN chmod u+x /usr/local/bin/init.sh

ENV LISTEN_PORT=8000
# EXPOSE 8000 2222
EXPOSE 8000

CMD ["python", "/code/manage.py", "runserver", "0.0.0.0:8000"]
ENTRYPOINT ["init.sh"]