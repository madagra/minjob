import logging
import logging.handlers
import os
import smtplib


def init_logger(log):

    # set default log root folder and debug level
    log_root = "./" if "HOME" not in os.environ else f"{os.environ['HOME']}/"
    log.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "[%(asctime)s - %(levelname)s] %(message)s"
    )

    # set handler output warnings and errors to file and revolve if size exceed 1GB
    log_path = log_root + ".minjob.log"
    fh = logging.handlers.RotatingFileHandler(log_path, maxBytes=pow(2, 30))
    fh.setFormatter(fmt=formatter)
    fh.setLevel(logging.INFO)
    log.addHandler(fh)

    # set handler output debug to errors to stdout
    ch = logging.StreamHandler()
    ch.setFormatter(fmt=formatter)
    ch.setLevel(logging.ERROR)
    log.addHandler(ch)

    return log


logger = init_logger(logging.getLogger("minjob"))


class MailNotifier:
    def __init__(self, config,
                 app_name="MyApp",
                 job_name="MyAppJob"):
        # TODO: use hashed username and passwords
        try:

            assert isinstance(config, dict)
            self.user = config["user"]
            self.password = config["password"]
            self.sender = self.user
            self.receivers = config["receivers"]
            self.app_name = app_name
            self.job_name = job_name
            self.smtp_server = config["server"] if "server" in config else "smtp.gmail.com"
        except AssertionError:
            logger.warning("Wrong email configuration: cannot send emails.")

    # driver routine for sending email notifications
    def send_email(self, subject, body):
        """
        Send an email using a secured SSL connection
        """
        try:
            mail_server = smtplib.SMTP_SSL(self.smtp_server, 465, timeout=30)
            mail_server.ehlo()
            mail_server.login(self.user, self.password)
            text = f"\nGreetings from {self.app_name} application!\n{body}"
            message = f"Subject: {subject}\n\n{text}"
            mail_server.sendmail(self.sender, self.receivers, message)
            mail_server.close()
        except Exception as ex:
            logger.error("ERROR initializing SMTP server: {}".format(ex))

    def abort(self, info):
        """
        Send an email following a fatal error
        """
        self.send_email(f"Exception caught in the {self.job_name} process of the {self.app_name} application.", info)
