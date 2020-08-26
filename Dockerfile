FROM ubuntu:latest

# Add the get_pricing script
ADD get_pricing.py /

# Install cron
RUN apt-get -y install cron

# Create the log file to be able to run tail
RUN touch /var/log/get_pricing.log

# Setup cron job (daily at midnight)
RUN (crontab -l ; echo "0 0 * * * python3 get_pricing.py >> /var/log/get_pricing.log") | crontab

# Run the command on container startup
CMD cron && tail -f /var/log/get_pricing.log
