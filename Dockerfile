FROM ubuntu:16.04

WORKDIR /app

COPY requirements.txt requirements.txt
RUN apt-get -y update && \
    apt-get -y install python3-pip \
     build-essential git cmake qt5-default libxml2 libxslt1.1 python-dev qtbase5-dev \
     qttools5-dev-tools libqt5clucene5 libqt5concurrent5 libqt5core5a libqt5dbus5 libqt5designer5 libqt5designercomponents5 libqt5feedback5 libqt5gui5 libqt5help5 libqt5multimedia5 libqt5network5 libqt5opengl5 libqt5opengl5-dev libqt5organizer5 libqt5positioning5 libqt5printsupport5 libqt5qml5 libqt5quick5 libqt5quickwidgets5 libqt5script5 libqt5scripttools5 libqt5sql5 libqt5sql5-sqlite libqt5svg5 libqt5test5 libqt5webkit5 libqt5widgets5 libqt5xml5 libqt5xmlpatterns5 libqt5xmlpatterns5-dev

RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "main.py"]