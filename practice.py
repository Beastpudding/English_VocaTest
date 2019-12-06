# 1. play again: 다시 풀고 싶을 때, 퀴즈 프로그램을 초기화하여 문제를 풀게 만듦
# 2. 랭킹시스템: 동일 이름은 응시를 할 수 없게 만들고, 랭킹시스템을 만들어서 사용자가 자신의 순위를 확인 할 수 있게 만듦
# 3. 시간 측정: 시간이 다지나면 남은 문제는 풀 수 없고 바로 결과창으로 넘어감
# 4. 틀린문제 보여주기: 틀린 문제를 응시가 끝난 결과창에서 보여줌으로써 틀린 문제를 확인하고 사용자가 공부할 수 있게 도와줌

import tkinter as screen
from tkinter import *
from tkinter import messagebox
import re

from MyDatabase import MyDatabase
import random

import collections

remaining = -1
class VocaTest:
    def __init__(self, Vocaroute):  #파일 불러오기 및 단어 리스트 생성
        self.db = MyDatabase(Vocaroute)
        self.wordList = self.db.getDataList()
        global q
        global answerList
        global real

    def startTest(self):  # 문제 리스트와 총 문제수 입력 받기
        self.numOfProblemIndex = 1
        wLen = len(self.wordList)  # 총 단어 수
        self.qCheck = []
        self.numOfProblems = 10 #문항 수: 10문항
        self.correctAnswerIndex = 0
        self.answerList=[]
        while self.numOfProblemIndex <= self.numOfProblems:
            qWordIndex = random.randint(0, wLen - 1)  # 랜덤 넘버로 문제와 정답이 있는 리스트 설정
            while qWordIndex in self.qCheck:
                qWordIndex = random.randint(0, wLen - 1)
            self.qCheck.append(qWordIndex)  # 출제가 된 문제는 qCheck에 넣어서 다른 문제와 겹치지 않게함
            qWord = self.wordList[qWordIndex][0]  # 문제단어 qWord로 설정

            self.correctAnswerIndex = random.randint(1, len(self.wordList[qWordIndex]) - 1)
            correctAnswer = self.wordList[qWordIndex][self.correctAnswerIndex]  # 문제의 정답을 랜덤으로 정함

            self.answerList = []
            while len(self.answerList) is not 4:  # 틀린보기 4개 선정
                index = random.randint(0, wLen - 1)
                if index is not qWordIndex:
                    word = self.wordList[index][random.randint(0, len(self.wordList[index]) - 1)]
                    self.answerList.append(word)
                self.answerList = list(set(self.answerList))

            randomIndex = random.randint(0, 4)  # 틀린보기 안에 무작위로 정답을 넣고
            self.answerList.insert(randomIndex, correctAnswer)  # 정답 번호를 설정한다
            self.correctAnswerIndex = randomIndex + 1

            answerList.append(self.answerList)
            real.append(self.correctAnswerIndex)
            q.append(qWord)

            self.numOfProblemIndex += 1

q=[] #문제리스트
answerList=[] #객관식답안 리스트
real=[] #문제당 답
wrongAnswer=[] #틀린문제(문제단어, 답 단어, 사용자가 선택한 단어)

user=VocaTest("VocaTest.xlsx") #퀴즈 시작전 위 빈칸 리스트들 채움.
user.startTest()

userID=["여성동"] #userID 중복 안되게 하기
userRanking={"Master": 10, }


class QuizScreen(screen.Tk): #3개(등록프레임, 퀴즈프레임, 결과프레임)의 프레임을 가두는 콘테이너

    def __init__(self, *args, **kwargs):
        screen.Tk.__init__(self, *args, **kwargs)
        container = screen.Frame(self)
        container.pack(side='top', fill='both', expand= True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (RegisterPage, QuizPage, ResultPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_Frame(RegisterPage)


    def show_Frame(self,cont): #프레임간 이동할 수 있는 함수
        frame = self.frames[cont]
        frame.tkraise()

    def play_again(self,cont): #한번더 플레이하기위해 위 채웠던 리스트들 초기화후 다시 채우기
        global q
        global answerList
        global real
        global wrongAnswer
        wrongAnswer = []
        q=[]
        answerList=[]
        real=[]
        user=VocaTest("VocaTest.xlsx")
        user.startTest()
        frame = self.frames[cont]
        frame.tkraise()


class RegisterPage(screen.Frame): #등록페이지

    def __init__(self, parent, controller):
        screen.Frame.__init__(self, parent)
        label1 = screen.Label(self, text="Put your ID on it buddy", font= ("Helvetica Bold", 24))
        label1.pack(padx=30,pady=30)
        str=StringVar()
        textbox = screen.Entry(self, textvariable=str)
        textbox.pack()
        check_button=screen.Button(self,text="ID Check",height='3',width='8',command = lambda:self.checking_ID(str,controller))
        check_button.pack()
        parent.bind('<Return>',lambda event: self.checking_ID(str, controller))

    def checking_ID(self,str,controller): #아이디 중복여부, null 값, blank space 값 오류메시지 띄우거나 등록하기.
        global userID, remaining
        remaining = 30
        self.user=str.get()
        p=re.compile("^\S+$")
        if self.user not in userID and p.match(self.user):
            userID.append(self.user)
            messagebox.showinfo("Successfully registered","Get ready and Press OK to start\n\n        Time Limit: 30s")
            controller.show_Frame(QuizPage)

        else:
            messagebox.showerror("Try Again", "You just put already existing ID or blank.")


class QuizPage(screen.Frame): #퀴즈페이지

    def __init__(self, parent, controller):
        screen.Frame.__init__(self, parent)
        self.opt_selected=IntVar()
        self.qn=0
        self.correct=0
        self.ques = self.create_q(self, self.qn)
        self.opts = self.create_options(self, 5)
        self.display_q(self.qn)
        button_1 = screen.Button(self, text="Next", command = lambda:self.next_btn(controller))
        button_1.pack(side=BOTTOM)
        self.label = screen.Label(self, text="", width=10)
        self.label.pack(side=RIGHT)
        self.countdown()
        self.controller=controller

    def countdown(self): #시간 카운트다운
        global remaining
        if remaining == 0:
            self.print_results()
            messagebox.showinfo("Time's Up!","You got {}".format(score))
            self.controller.show_Frame(ResultPage)
        else:
            self.label.configure(text="%d" % remaining)
            remaining -= 1
            self.after(1000, self.countdown)

    def create_q(self, parent, qn):
        label_1=screen.Label(self,text=q[qn])
        label_1.pack(side=TOP)
        return label_1

    def create_options(self, parent, n):
        b_val=0
        b=[]
        while b_val<n:
            btn_1 = screen.Radiobutton(self, text="교수님 OOP수업 너무재밌었어요!", variable=self.opt_selected, value = b_val+1)
            b.append(btn_1)
            btn_1.pack(side=TOP,anchor="w")
            b_val +=1
        return b

    def display_q(self, qn):
        b_val = 0
        self.opt_selected.set(0)
        self.ques["text"]=q[qn]
        for op in answerList[qn]:
            self.opts[b_val]["text"] = op
            b_val += 1

    def check_q(self,qn):
        global wrongAnswer
        if self.opt_selected.get() == real[qn]:
            return True
        else:
            wronglist=[q[self.qn], answerList[self.qn][real[qn]-1], answerList[self.qn][self.opt_selected.get()-1]]
            wrongAnswer.append(wronglist)
            return False

    def print_results(self):
        global score
        global userRanking
        score="{} / {}".format(self.correct, len(q))
        userRanking.update({userID[-1]:self.correct})

    def next_btn(self,controller): #다음화면 넘어가기 함수, 다끝나면 몇점인지 알려줌
        global remaining
        if self.check_q(self.qn):
            self.correct+=1
        self.qn += 1
        if self.qn >= len(q):
            self.print_results()
            remaining = -1     #시험이 끝나면 시간을 -1로 설정해서 Time's up이 뜨지 않게 한다. Play again을 누르면 checking_ID에서 다시 30으로 설정됨
            messagebox.showinfo("Well Done","You got {}".format(score))
            controller.show_Frame(ResultPage)
            self.qn = 0   #play_again을 위한 reset
        else:
            self.display_q(self.qn)


class ResultPage(screen.Frame):
    def __init__(self, parent, controller):
        screen.Frame.__init__(self, parent)
        label4 = screen.Label(self, text="Do you wanna play again?", font=("Helvetica", 16))
        label4.pack()
        self.label5 = screen.Label(self, text=" ", font=("Helvetica Bold",11))
        self.label5.pack()
        # self.label6 = screen.Label(self, text=" ", font=("Helvetica Bold", 11))
        # self.label6.pack()
        button4 = screen.Button(self, text="Play again", height='2', width='15', command=lambda: controller.play_again(RegisterPage))
        button4.pack()
        button5= screen.Button(self, text="Check Wrong Answers", height='2', width='15', command= lambda: self.show_wrong())
        button5.pack()
        button6= screen.Button(self, text="Ranking", height='2', width='15', command= lambda: self.show_ranking())
        button6.pack()
        button7 = screen.Button(self, text="END", height='2', width='15', command=controller.quit)
        button7.pack()

    def show_wrong(self): #틀린문제 보여주기
        jax=""
        for i,k in enumerate(wrongAnswer):
            jax+=("Question No.{} : {}\n Right Answer: {}\n Your Answer: {}\n\n".format(i+1, k[0], k[1], k[2]))
        self.label5.configure(text=jax)

    def show_ranking(self):
        global userRanking
        sexyjax=""
        userRanking=sorted(userRanking.items(), key=lambda kv:kv[1], reverse=True)
        userRanking=collections.OrderedDict(userRanking)
        for i,(k,v) in enumerate(userRanking.items()):
            sexyjax+="Rank {}:  {}      Score: {}\n".format(i+1,k,v)
        self.label5.configure(text = sexyjax)


app= QuizScreen()
app.mainloop()