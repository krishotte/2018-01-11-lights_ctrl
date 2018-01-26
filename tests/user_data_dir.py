#import kivy
from kivy.app import App

class Lights_Ctrl(App):                        #app class
    def build(self):
        print(self.user_data_dir)
            
if __name__ == "__main__":                      #runs app
    Lights_Ctrl().run()