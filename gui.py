import sys
import os
import pygame as pg
import pygame.camera as pgCam
import datetime
from PIL import Image
from settings import *

# Camera 
pgCam.init()
cam_list = pgCam.list_cameras()
cam = pgCam.Camera(cam_list[0],(800,480),"RGB")
#rotate the camera
os.system('v4l2-ctl --set-ctrl=rotate=180')
cam.start()


#globals:
timerTickEvent       = pg.USEREVENT + 0
startTimerEvent      = pg.USEREVENT + 1
startMainScreenEvent = pg.USEREVENT + 2
startCameraEvent     = pg.USEREVENT + 3
startTalkingEvent    = pg.USEREVENT + 4
cameraTickEvent      = pg.USEREVENT + 5

class MusicStationGUI:
    def __init__(self):
        # PyGame screen
        pg.init()
        self.screen = pg.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT), pg.NOFRAME)
        pg.display.set_caption("MusicStation")
        pg.mouse.set_visible(False)
        self.clock = pg.time.Clock()
        self.gsm   = GUIScreenManager('main')
        self.splashScreen    = SplashScreen(self.screen, self.gsm)
        self.mainScreen      = MainScreen(self.screen, self.gsm)
        self.timerScreen     = CountdownScreen(self.screen, self.gsm)
        self.talkingScreen   = TalkingScreen(self.screen, self.gsm)
        self.cameraScreen    = CameraScreen(self.screen, self.gsm)
        self.screens = {'main':self.mainScreen, 
                        'timer':self.timerScreen, 
                        'talking':self.talkingScreen, 
                        'photo':self.cameraScreen}
        self.countDownCounter = 0
        self.cameraCounter    = 5

    def mainLoop(self):
        while True:
            # handle the events
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == startMainScreenEvent:
                    self.gsm.setActiveScreen('main')
                if event.type == startTimerEvent:
                    self.timerScreen.startTimerEvent()
                    self.gsm.setActiveScreen('timer')
                if event.type == startTalkingEvent:
                    self.gsm.setActiveScreen('talking')
                if event.type == startCameraEvent:
                    self.cameraScreen.startTimerEvent()
                    self.gsm.setActiveScreen('photo')
                # Handle the timer event
                if event.type == timerTickEvent:
                    if self.countDownCounter > 0:
                        self.countDownCounter -= 1
                    else:
                        self.countDownCounter = 0
                    self.timerScreen.setCountDownValue(self.countDownCounter)
                # Handle the camera countdown event
                if event.type == cameraTickEvent:
                    if self.cameraCounter > 0:
                        self.cameraCounter -= 1
                    else:
                        self.cameraCounter = 0
                    self.cameraScreen.setCountDownValue(self.cameraCounter)


            # Display the active screen content 
            self.screens[self.gsm.getActiveScreen()].run()
            # Update the pygame screen
            pg.display.flip()
            pg.display.update()
            self.clock.tick(SCREEN_FPS) # update every 60 seconds

    def setTimerValue(self, timer):
        self.countDownCounter = timer
        self.timerScreen.setCountDownValue(self.countDownCounter)
    
    def setConditions(self, conditions):
        self.mainScreen.weatherConditions = conditions
    
    def setSenosorsReadings(self, readings):
        self.mainScreen.roomTemperature = readings[0]
        self.mainScreen.roomHumidity = readings[1]

    # loaders (gui elements)
    def loadMoods(self):
        '''
            loads a gif file from given path and 
            append each frame to a list

            @return: a dict of lists of frames extracted from the given gif
        '''
        frame_dict = {}
        for mood in JARVIS_MOOD_GIFS:
            frame_lst = []
            path = "./img/moods/" + mood + ".gif"
            gif  = Image.open(path)
            for frame_idx in range(gif.n_frames):
                gif.seek(frame_idx)
                frame_rgba = gif.convert("RGBA")
                image = pg.image.fromstring(
                    frame_rgba.tobytes(), 
                    frame_rgba.size,
                    frame_rgba.mode
                )
                frame_lst.append(image)
            frame_dict[mood] = frame_lst

        self.talkingScreen.setMoodDict(frame_dict)

class SplashScreen:
    def __init__(self, display, guiScreenManager):
        self.display          = display
        self.guiScreenManager = guiScreenManager
        self.loadingCounter   = 0
        self.logo = pg.image.load("./img/misc/logo.png").convert_alpha()
        self.progressMsgFont  = pg.font.SysFont(JARVIS_FONT_1, SPLASH_TEXT_SIZE, True, False)
        
    def show(self):
        #fill background
        self.display.fill(GUI_BLACK)
        self.display.blit(self.logo, SPLASH_LOGO_POS)
        progText = self.progressMsgFont.render('Loading...', True, SPLASH_TEXT_COLOR)
        progRect = progText.get_rect()
        progRect.topleft = SPLASH_TEXT_POS
        self.display.blit(progText, progRect)
        pg.display.flip()
        pg.display.update()

    def updateProgressMessage(self, msg):
        progText = self.progressMsgFont.render(msg, True, SPLASH_TEXT_COLOR)
        progRect = progText.get_rect()
        progRect.topleft = SPLASH_TEXT_POS
        # clear the rectangle
        pg.draw.rect(self.display, GUI_BLACK, pg.Rect(SPLASH_TEXT_RECT))
        self.display.blit(progText, progRect)
        pg.display.flip()
        pg.display.update()
        

class MainScreen:
    def __init__(self, display, guiScreenManager):
        self.display = display
        self.guiScreenManager = guiScreenManager
        self.timer = pg.time.Clock()
        self.roomTemperature = 0
        self.roomHumidity = 0
        self.weatherConditions = []
        self.timeFont = pg.font.SysFont(MAIN_FONT, TIME_TEXT_SIZE, True, False)
        self.dateFont = pg.font.SysFont(MAIN_FONT, DATE_TEXT_SIZE, True, False)
        self.dateFont.set_italic(True)
        self.condFont = pg.font.SysFont(MAIN_FONT, COND_TEXT_SIZE, True, False)
        self.tempFont = pg.font.SysFont(MAIN_FONT, TEMP_TEXT_SIZE, True, False)
        self.locFont = pg.font.SysFont(MAIN_FONT, LOC_TEXT_SIZE, True, False)
        self.phwFont = pg.font.SysFont(MAIN_FONT, INFO_TEXT_SIZE, True, False)
        self.genfont = pg.font.SysFont(MAIN_FONT, INFO_TEXT_SIZE, True, False)


    def run(self):
        self.display.fill(GUI_BLACK)
        currTime = datetime.datetime.now()
        self.displayTime(currTime)
        self.displayDate(currTime)
        self.displayRoomReadings(self.roomTemperature, self.roomHumidity)
        self.displayWeatherReadings(self.weatherConditions)

    def displayTime(self, curTime):
        hr  = curTime.strftime('%H')
        min = curTime.strftime('%M')
        curTimeFormatted = f"{hr}:{min}"
        timeText = self.timeFont.render(curTimeFormatted, True, TIME_TEXT_COLOR)
        timeRect = timeText.get_rect()
        timeRect.topleft = TIME_TEXT_POS
        self.display.blit(timeText, timeRect)

    def displayDate(self, curTime):
        wday  = curTime.strftime('%a')
        day   = curTime.strftime('%-d')
        month = curTime.strftime('%b')
        curTimeFormatted = f"{wday}, {day} {month}"
        dateText = self.dateFont.render(curTimeFormatted, True, DATE_TEXT_COLOR)
        dateRect = dateText.get_rect()
        dateRect.topleft = DATE_TEXT_POS
        self.display.blit(dateText, dateRect)

    def displayWeatherReadings(self, conditions):
        try:
            condIcon = pg.image.load("./img/weather/"+conditions[0]).convert_alpha()
            self.display.blit(condIcon, COND_ICON_POS)
            condText = self.condFont.render(conditions[2].upper(), True, GUI_WHITE)
            condRect = condText.get_rect()
            # calculate the position for the text (depending on length)
            COND_TEXT_xPOS   = COND_ICON_POS[0] + ((condIcon.get_height() - condRect.width)/2)
            condRect.topleft = (COND_TEXT_xPOS, COND_TEXT_yPOS)
            self.display.blit(condText,condRect)
            tempText = self.tempFont.render(conditions[3], True, GUI_WHITE)
            tempRect = tempText.get_rect()
            TEMP_TEXT_xPOS   = COND_ICON_POS[0] + ((condIcon.get_height() - tempRect.width)/2)
            tempRect.topleft = (TEMP_TEXT_xPOS, TEMP_TEXT_yPOS)
            self.display.blit(tempText,tempRect)
            locIcon = pg.image.load("./img/misc/location.png").convert_alpha()
            self.display.blit(locIcon, LOC_ICON_POS)
            locText = self.locFont.render(conditions[7], True, GUI_WHITE)
            locRect = locText.get_rect()
            locRect.topleft = LOC_TEXT_POS
            self.display.blit(locText,locRect)
            precIcon = pg.image.load("./img/misc/precipitation.png").convert_alpha()
            self.display.blit(precIcon, PREC_ICON_POS)
            precText = self.phwFont.render(conditions[5], True, GUI_WHITE)
            precRect = precText.get_rect()
            precRect.topleft = PREC_TEXT_POS
            self.display.blit(precText,precRect)
            humIcon = pg.image.load("./img/misc/humid.png").convert_alpha()
            self.display.blit(humIcon, HUM_ICON_POS)
            humText = self.phwFont.render(conditions[4], True, GUI_WHITE)
            humRect = humText.get_rect()
            humRect.topleft = HUM_TEXT_POS
            self.display.blit(humText,humRect)
            windIcon = pg.image.load("./img/misc/wind.png").convert_alpha()
            self.display.blit(windIcon, WIND_ICON_POS)
            windText = self.phwFont.render(conditions[6], True, GUI_WHITE)
            windRect = windText.get_rect()
            windRect.topleft = WIND_TEXT_POS
            self.display.blit(windText,windRect)
        except: #Show only default png if no data available 
            condIcon = pg.image.load("./img/weather/default.png").convert_alpha()
            self.display.blit(condIcon, COND_ICON_POS)

    def displayRoomReadings(self, temp, hum):
        tempIcon = pg.image.load("./img/misc/temperature.png").convert_alpha()
        self.display.blit(tempIcon, S_TEMP_ICON_POS)
        tempText = self.genfont.render(str(int(temp))+"°C", True, GUI_WHITE)
        tempRect = tempText.get_rect()
        tempRect.topleft = S_TEMP_TEXT_POS
        self.display.blit(tempText, tempRect)
        humIcon =  pg.image.load("./img/misc/humidity.png").convert_alpha()
        self.display.blit(humIcon, S_HUM_ICON_POS)
        humText = self.genfont.render(str(int(hum))+"%", True, GUI_WHITE)
        humRect = humText.get_rect()
        humRect.topleft = S_HUM_TEXT_POS
        self.display.blit(humText, humRect)
    
    # Setter function for room readings
    def updateReadings(self, temp, hum):
        self.roomHumidity = hum
        self.roomTemperature = temp
    # Setter function for weather conditions
    def updateConditions(self, conditions):
        self.weatherConditions = conditions

class CountdownScreen:
    def __init__(self, display, guiScreenManager):
        self.display = display
        self.guiScreenManager = guiScreenManager
        self.countDownCounter = 0
        self.timerFont = pg.font.SysFont(MAIN_FONT, TIMER_TEXT_SIZE, True, False)

    def run(self):
        if self.countDownCounter == 0:
            self.display.fill(GUI_ORANGE)
        else: # black screen
            self.display.fill(GUI_BLACK)
        
        if self.countDownCounter == 1:
            # play alarm sound
            pg.mixer.init()
            pg.mixer.music.load(TIMER_ALARM_FILE)
            pg.mixer.music.play()
        # Convert seconds to time format
        curTimerFormatted = str(datetime.timedelta(seconds=self.countDownCounter))
        timerText = self.timerFont.render(curTimerFormatted, True, TIMER_TEXT_COLOR)
        timerRect = timerText.get_rect()
        TIMER_TEXT_xPOS   =(SCREEN_WIDTH - timerRect.width)/2
        timerRect.topleft = (TIMER_TEXT_xPOS, TIMER_TEXT_yPOS)
        self.display.blit(timerText, timerRect)
    
    def setCountDownValue(self, value):
        self.countDownCounter = value
    
    def startTimerEvent(self):
        pg.time.set_timer(timerTickEvent, 1000)

class TalkingScreen:
    def __init__(self, display, guiScreenManager, loopMood = False):
        self.display = display
        self.guiScreenManager = guiScreenManager
        self.loopMood = loopMood
        self.mood = "wakeup"
        self.mood_index = 0
        self.mood_frames = {}
        self.request = ""
        self.message = ""
        self.message_index = 0
        self.message_speed = 3
        self.snip_font = pg.font.SysFont(JARVIS_FONT_1, TALKING_TEXT_SIZE, False, False)

    def run(self):
        self.display.fill(GUI_BLUE)
        # loop through the gif frames
        if self.mood_index < len(self.mood_frames[self.mood]) - 1:
            self.mood_index += 1
        else:
            self.mood_index = 0 if self.loopMood else len(self.mood_frames[self.mood]) - 1

        curFrame = self.mood_frames[self.mood][self.mood_index].convert_alpha()
        self.display.blit(curFrame, MOOD_EYE_1_POS)
        #Double the circle for an eye effect!!!
        self.display.blit(curFrame, MOOD_EYE_2_POS)
        
        # loop through the message letters
        if self.message_index < self.message_speed * len(self.message) - 1:
            self.message_index += 1
        else: 
             self.message_index = self.message_speed * len(self.message) - 1
        
        text = self.message[0:self.message_index//self.message_speed]
        rect = pg.Rect(TALKING_TEXT_X, TALKING_TEXT_Y, TALKING_TEXT_W, TALKING_TEXT_H)
        self.drawText(rect, text, self.snip_font, TALKING_TEXT_COLOR)
    
    def drawText(self, rect, text, font, color):
        '''
            Wraps a text inside a defined rectangle
            @param rect: pygame rectangle to wrap the text within
            @param text: string to be wrapped
            @param font: pygame font of the text
            @param color: text color (R,G,B)
        '''
        y = rect.top
        lineSpacing = -2

        while text:
            i = 1

            # determine if the row of text will be outside our area
            if y + TALKING_TEXT_SIZE > rect.bottom:
                break

            # determine maximum width of line
            while font.size(text[:i])[0] < rect.width and i < len(text):
                i += 1

            # if we've wrapped the text, then adjust the wrap to the last word      
            if i < len(text): 
                i = text.rfind(" ", 0, i) + 1

            # render the line and blit it to the surface
            image = font.render(text[:i], True, color)

            self.display.blit(image, (rect.left, y))
            y += TALKING_TEXT_SIZE + lineSpacing

            # remove the text we just blitted
            text = text[i:]

    def setLoopMood(self, state):
        '''
            enable/disbale continuously playing the mood gif
            @param state: bool => 
            True = enable loop / False = disable loop
        '''
        self.loopMood = state
    
    def setMood(self, new_mood):
        self.mood = new_mood

    def getMood(self):
        return self.mood
    
    def setMoodDict(self, mood_dict):
        self.mood_frames = mood_dict
    
    def setScrollingTextSpeed(self, speed):
        self.message_speed = speed
    
    def setMessageText(self, text):
        self.message = text

    def setRequestText(self, text):
        self.request = text

class CameraScreen:
    def __init__(self, display, guiScreenManager):
        self.display = display
        self.guiScreenManager = guiScreenManager
        self.countDownCounter = 6 # 5 seconds
        self.snapshot = pg.surface.Surface((800,480), 0, self.display)
        self.timerFont = pg.font.SysFont(MAIN_FONT, TIMER_TEXT_SIZE, False, False)

    def run(self):
        #fill background
        self.display.fill(GUI_BLACK)

        if self.countDownCounter == 1:
            # take a photo
            self.takePhoto()
            
        elif self.countDownCounter == 0:
            # display the taken photo
            self.displayPhotoAndFrame()
        else:
            self.displayCameraFeed()
            self.displayCountdown()

    def setCountDownValue(self, value):
        self.countDownCounter = value

    def startTimerEvent(self):
        pg.time.set_timer(cameraTickEvent, 1000)
    
    def displayCountdown(self):
        # display counter
        curTimerFormatted = str(self.countDownCounter - 1)
        timerText = self.timerFont.render(curTimerFormatted, True, TIMER_TEXT_COLOR)
        timerRect = timerText.get_rect()
        TIMER_TEXT_xPOS   =(SCREEN_WIDTH - timerRect.width)/2
        timerRect.topleft = (TIMER_TEXT_xPOS, TIMER_TEXT_yPOS)
        self.display.blit(timerText, timerRect)
    
    def takePhoto(self):
        # play shutter sound
        pg.mixer.init()
        pg.mixer.music.load(CAM_SHUTTER_FILE)
        pg.mixer.music.play()
        if cam.query_image():
            self.stamp = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
            self.snapshot = cam.get_image(self.snapshot)
            pg.image.save(self.snapshot, "./camera/image_"+ self.stamp +".jpg")

    def displayPhotoAndFrame(self):
        frame = pg.image.load("./img/misc/frame.png").convert_alpha()
        image = pg.image.load("./camera/image_"+ self.stamp +".jpg")
        image = pg.transform.scale(image, (481,323))
        self.display.blit(image, (159,39))
        self.display.blit(frame, (0,0))

    def displayCameraFeed(self):
        frame = cam.get_image()
        self.display.blit(frame,(0,0))

class GUIScreenManager:
    def __init__(self, currentScreen):
        self.currentScreen = currentScreen
    
    def setActiveScreen(self, activeScreen):
        self.currentScreen = activeScreen
    def getActiveScreen(self):
        return self.currentScreen
    
