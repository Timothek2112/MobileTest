from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.checkbox import CheckBox
from kivy.storage.jsonstore import JsonStore
from random import shuffle
import datetime
import random
import copy
from enum import Enum
from kivy.properties import DictProperty, NumericProperty, ListProperty

Builder.load_string("""
<ScreenManagement>:
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            pos: self.pos
            size: self.size
    ResultScreen:
        correct: testScreen.correct_count
<MainScreen>:
    name: "main screen"
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            pos: self.pos
            size: self.size
    
    FloatLayout:
        Label:
            text:'Тест на знание Новосибирска'
            color: 0 , 0 , 0 , 1
            pos_hint: {'center_x': .5, 'center_y': .9}
            size_hint: 1,.1
            font_size: 25
        
        Image:
            source:'./Images/Новосиб.jpeg'
            pos_hint: {'center_x': 0.5, 'center_y': 0.6}

        Button:
            text:'Начать'
            size_hint: 1, .1
            pos_hint: {'center_x': 0.5, 'center_y': 0.2}
            on_press: root.start_test()

        Button:
            text: 'Предыдущие результаты'
            size_hint: 1, .1
            pos_hint: {'center_x': .5, 'center_y': .3} 
            on_press: root.show_results()

<TestScreen>:
    id: testScreen
    name: "test screen"
    canvas.before:
        Color:
            rgba: 1,1,1,1
        Rectangle:
            pos: self.pos
            size: self.size[0] * 2, self.size[1]
    FloatLayout:
        id: float
        Label:
            id: number
            text:'Вопрос номер 1'
            color: 0 , 0 , 0 , 1
            pos_hint: {'center_x': .5, 'center_y': 0.97}
            size_hint: 1,.1
            font_size: 25

        Image:
            id: illustrate
            source: './Images/Новосиб.jpeg'
            size_hint: 0.8, 0.8
            pos_hint: {'center_x': 0.5, 'center_y': 0.7}

        Label:
            id: qLabel
            text:'Вопрос'
            color: 0 , 0 , 0 , 1    
            pos_hint: {'center_x': .5, 'center_y': .9}    
            size_hint: 1,.3
            font_size: 15   
            halign: "center"  

<ResultScreen>:
    name: "result screen"
    canvas.before:
        Color:
            rgba: 1,1,1,1
        Rectangle:
            pos: self.pos
            size: self.size
    FloatLayout:
        Label:
            id: resultLbl
            text:'Чел харош'
            color: 0,0,0,1
            pos_hint: {'center_x': .5, 'center_y': .5}
            size_hint: 1, .1 
            halign: 'center'

<SavedResults>:
    name: "saved screen"
    canvas.before:
        Color:
            rgba: 1,1,1,1
        Rectangle:
            pos: self.pos
            size: self.size
""")

store = JsonStore("storage")

qTag = 'question'
vTag = 'variants'
aTag = 'answer'
iTag = 'image'
questions = [
    {qTag: 'Какое прежнее название\nНовосибирска?', vTag: ['Ново-николаевск', 'Ново-андрейск', 'Ново-тихинск'], aTag: 0, iTag: './Images/Название.jpg'},
    {qTag: 'Какое место занимает город\nпо численности населения?', vTag: ['Седьмое', 'Второе', 'Третье'], aTag: 2, iTag: './Images/Жители.jpeg'},
    {qTag: 'Какова длина Красного проспекта?', vTag: ['10 км', '7 км', '4 км'], aTag: 1, iTag: './Images/Красный.jpg'},
    {qTag: 'Какой рекорд поставили местные\nповара ко дню города в 2013-м году?', vTag: ['Колбаса весом 50 кг', 'Гамбургер диаметром 1 метр', 'Пирожное-суфле длиной почти\n100 метров'], aTag: 2, iTag: './Images/Повара.jpg'},
    {qTag: 'Музеем какого космического светила\nизвестен город?', vTag: ['Луны', 'Солнца', 'Путеводной звезды'], aTag: 1, iTag: './Images/МузейСолнца.jpg'},
    {qTag: 'Каков размер главной площади Новосибирска?', vTag: ['500 кв км', '800 кв км', '200 кв км'], aTag: 0, iTag: './Images/Площадь.png'},
    {qTag: 'Как называется уникальное животное,\nпредставленное в Новосибирском зоопарке?', vTag: ['Лигр', 'Барсук', 'Капибара'], aTag: 0, iTag: './Images/Зоо.jpg'},
    {qTag: 'Как называется самая большая река города?', vTag: ['Иня', 'Обь', 'Тула'], aTag: 1, iTag: './Images/Река.jpg'},
    {qTag: 'На сколько каждый день увеличивается\nнаселение города за счёт маятниковой миграции?', vTag: ['100 чел', '200 чел', '1000 чел'], aTag: 1, iTag: './Images/Миграция.jpg'},
    {qTag: 'Какой мост города имеет самый большой\n арочный пролёт?', vTag: ['Комсомольский', 'Метромост', 'Бугринский'], aTag: 2, iTag: './Image/Мосты вечером.jpg'},
    {qTag: 'Когда основался Новосибирск?', vTag: ['1923', '1917', '1893'], aTag: 2, iTag: './Images/Старый.jpg'},
    {qTag: 'Как называются жители Новосибирска?', vTag: ['Новосибирцы', 'Новосибиряки', 'Новосибирякцы'], aTag: 0, iTag: './Images/Численность.jpg'},
    {qTag: 'Что проходило через Новосибирск до\n20-х годов XX века, что создавало неудобства\nдля жителей города?', vTag: ['Две железные дороги', 'Два канала', 'Два часовых пояса'], aTag: 2, iTag: './Images/Часовые пояса.jpg'},
    {qTag: 'Сооружение какого заведения в Новосибирске\nявляется самым крупным в России\nи 2-м в мире?', vTag: ['Театра', 'Аэропорта', 'Кинотеатра'], aTag: 0, iTag: './Images/Кино.jpg'},
    {qTag: 'Какие три цвета расположились на флаге города?', vTag: ['Белый, синий, зеленый', 'Белый, синий, красный', 'Зеленый, черный, фиолетовый'], aTag: 1, iTag: './Images/flag.jpg'},
]

answers_cb = []
answer_lbl = []
questions_count = len(questions)




class SavedScreen(Screen):
    def on_enter(self, *args):
        for i in range(store.get("count").get("count")):
            print(i)

class ResultScreen(Screen):

    def on_enter(self, *args):
        percent = self.manager.screens[1].correct_count /  questions_count
        correct_count = self.manager.screens[1].correct_count
        self.manager.screens[2].ids.resultLbl.text = "Вы ответили правильно на {} из {} вопросов,\nЭто {}%".format(correct_count, questions_count, percent)
        self.save_result(correct_count, percent)
        Clock.schedule_once(self.to_main, 10)
        
    def save_result(self, correct_count, percent):
        if not store.exists("count"):
            store.put("count", count=-1)
        count = store.get("count").get("count") + 1
        store.put(count, correct_count_saved=correct_count, questions_count_saved=questions_count, percent_saved=percent)
        store.put("count", count=count)

    def to_main(self, instance):
        self.manager.current = "main screen"

class MainScreen(Screen):
    def start_test(self):
        self.manager.transition= SlideTransition(direction="right")
        self.manager.current = "test screen"

    def show_results(self):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = "saved screen"

class TestScreen(Screen):
    current_question = DictProperty(None)
    answers_count = NumericProperty(0)
    questions_pop = ListProperty(None)
    correct_count = NumericProperty(0)

    def on_enter(self, *args):
        self.questions_pop = copy.deepcopy(questions)
        self.answers_count += 1
        self.remove_widgets()
        self.generate_page()
        self.generate_answers(self.current_question.get(vTag))

    def generate_page(self):
        self.current_question = random.choice(self.questions_pop)
        questions.pop(self.questions_pop.index(self.current_question))
        self.manager.screens[1].ids.number.text = 'Вопрос номер {}'.format(self.answers_count)
        self.manager.screens[1].ids.illustrate.source = self.current_question.get(iTag)
        self.manager.screens[1].ids.qLabel.text = self.current_question.get(qTag)

    def generate_answers(self, answers: list):
        for i in range(len(answers)):
            cb = CheckBox(pos_hint={'center_x': .1, 'center_y': .5 - (i / 10)}, size_hint=(.1, .1), color=(0,.4,0,1), on_press=self.check_answer)
            lbl = Label(pos_hint={'center_x': .5, 'center_y': .5 - (i / 10)}, size_hint=(0.9, .3), color=(0,0,0,1), text=answers[i])
            self.add_widget(cb)
            self.add_widget(lbl)
            answers_cb.append(cb)
            answer_lbl.append(lbl)

    def check_answer(self, instance):
        for i in range(len(answers_cb)):
            answers_cb[i].disabled = True # Блокируем все чекбоксы
            if answers_cb[i].active: # Выбранный checkbox
                if i == self.current_question.get(aTag): # Правильно
                    answer_lbl[i].color=(0,1,0,1)
                    self.correct_count += 1
                else: # Неправильно
                    answer_lbl[i].color=(1,0,0,1)
            if i == self.current_question.get(aTag): # Отмечаем правильный ответ
                answer_lbl[i].color=(0,1,0,1)
        self.next()

    def next(self):
        if self.answers_count < questions_count:
            Clock.schedule_once(self.next_question, 1)
        else:
            self.manager.current = 'result'

    def next_question(self, instance):
        self.on_enter()

    def remove_widgets(self):
        for i in answer_lbl:
            self.remove_widget(i)
        for i in answers_cb:
            self.remove_widget(i)
        answer_lbl.clear()
        answers_cb.clear()

    def reset(self):
        self.answers_count = 0
        self.questions_pop = []
        self.correct_count = 0


class MyApp(App):
    def build(self):
        screen_manager = ScreenManager()
        main = MainScreen()
        test = TestScreen()
        result = ResultScreen(name='result')
        saved = SavedScreen(name = 'saved screen')
        screen_manager.add_widget(main)
        screen_manager.add_widget(test)
        screen_manager.add_widget(result)
        screen_manager.add_widget(saved)
        
        return screen_manager

if __name__ == "__main__":
    app = MyApp()
    app.run()