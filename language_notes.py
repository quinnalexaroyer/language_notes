import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import sqlite3

class LanguageNotes:
	def __init__(self):
		self.root = tk.Tk()
		self.conn = sqlite3.connect("language_notes.db")
		self.c = self.conn.cursor()
		self.layouts = {}
		self.wvar = {}
		self.values = {}
		self.drawGuis()
		self.root.geometry("750x800+1000+50")
		self.root.mainloop()
	def drawGuis(self):
		self.drawMenuBar()
		self.chooseLanguageGui()
		self.viewWordGui()
		self.editWordGui()
		self.editContextGui()
		self.editReplaceGui()
		self.layouts["ChooseLanguage"].grid()
		self.layouts["active"] = self.layouts["ChooseLanguage"]
	def drawMenuBar(self):
		self.menubar = tk.Menu(self.root)
		self.root.config(menu=self.menubar)
		optionsMenu = tk.Menu(self.menubar,tearoff=0)
		optionsMenu.add_command(label="Edit Word",command=self.startEditWord)
		optionsMenu.add_command(label="Add Word",command=self.addWord)
		optionsMenu.add_command(label="Edit Context",command=self.startEditContext)
		optionsMenu.add_command(label="Add Context",command=self.addContext)
		optionsMenu.add_command(label="Edit Replacement Texts",command=self.startEditReplace)
		optionsMenu.add_command(label="Add Replacement Texts",command=self.addReplace)
		self.menubar.add_cascade(label="Options",menu=optionsMenu)
		self.menubar.entryconfig("Options",state="disabled")
	def chooseLanguageGui(self):
		layout = tk.Frame(self.root)
		self.layouts["ChooseLanguage"] = layout
		menuVar = tk.IntVar()
		langNameVar = tk.StringVar()
		theMenu = tk.OptionMenu(layout,menuVar,0)
		def addLanguage():
			nonlocal langNameVar, theMenu, layout
			self.c.execute("INSERT INTO languages (name) VALUES (?)", (langNameVar.get(),))
			self.conn.commit()
			newLangID = self.c.lastrowid
			theMenu["menu"].add_command(label=langNameVar.get(), command=tk._setit(menuVar, newLangID))
		self.c.execute("SELECT * FROM languages ORDER BY name")
		for i in self.c.fetchall():
			theMenu["menu"].add_command(label=i[1], command=tk._setit(menuVar, i[0]))
		theButton = tk.Button(layout, text="Use Language", command=lambda:self.useLanguage(menuVar.get()))
		theMenu.grid(row=0,column=0)
		theButton.grid(row=1,column=0)
		tk.Entry(layout, textvariable=langNameVar).grid(row=2,column=0)
		tk.Button(layout, text="Add Language", command=addLanguage).grid(row=3,column=0)
	def viewWordGui(self):
		layout = tk.Frame(self.root)
		self.layouts["ViewWord"] = layout
		tk.Button(layout, text="Search", command=lambda:self.searchWord(searchVar.get())).grid(row=0,column=0)
		searchVar = tk.StringVar()
		self.wvar["ViewSearch"] = searchVar
		tk.Entry(layout, textvariable=searchVar).grid(row=0,column=1)
		radioVar = tk.IntVar()
		self.wvar["SelectWordVar"] = radioVar
		radioFrame = tk.Frame(layout,height=100,width=300)
		radioFrame.grid(row=1,column=0,columnspan=2)
		self.wvar["SelectWordFrame"] = radioFrame
		self.wvar["SelectWordRadio"] = []
		wordFrame = tk.Frame(layout)
		wordVar = tk.StringVar()
		self.wvar["ViewWord"] = wordVar
		tk.Frame(layout, height=1, bg="black").grid(row=2,column=0,columnspan=2,sticky="nsew")
		tk.Label(wordFrame, textvariable=wordVar, font="Times 24").grid(row=0,column=0,rowspan=2)
		speechVar = tk.StringVar()
		self.wvar["ViewSpeech"] = speechVar
		tk.Label(wordFrame, textvariable=speechVar).grid(row=0,column=1)
		glossVar = tk.StringVar()
		self.wvar["ViewGloss"] = glossVar
		tk.Label(wordFrame, textvariable=glossVar).grid(row=1,column=1)
		wordFrame.grid(row=3,column=0,columnspan=2)
		tk.Label(layout, text="Translation").grid(row=4, column=0)
		translationText = ScrolledText(layout, height=5, width=80)
		translationText.grid(row=4,column=1)
		self.wvar["ViewTranslation"] = translationText
		translationText.config(state=tk.DISABLED)
		pageFrame = tk.Frame(layout)
		pageFrame.grid(row=5,column=0,columnspan=2)
		pageVar = tk.StringVar()
		pageVar.set("1 / 0")
		self.wvar["pageVar"] = pageVar
		tk.Label(layout,text="Context").grid(row=6,column=0)
		contextText = ScrolledText(layout, height=5, width=80)
		contextText.grid(row=6,column=1,columnspan=2)
		self.wvar["ViewContext"] = contextText
		contextText.config(state=tk.DISABLED)
		tk.Label(layout,text="Source").grid(row=7,column=0)
		sourceText = ScrolledText(layout, height=5, width=80)
		sourceText.grid(row=7,column=1,columnspan=2)
		self.wvar["ViewSource"] = sourceText
		sourceText.config(state=tk.DISABLED)
		def nextPage():
			nonlocal pageVar
			pp = pageVar.get().split(" / ")
			if int(pp[0]) < int(pp[1]):
				self.c.execute("SELECT * FROM contexts WHERE word_id=? ORDER BY id LIMIT ?,1", (self.word_id,int(pp[0])))
				r = self.c.fetchone()
				if r is not None:
					if r[2] is None:
						r = list(r)
						r[2] = ""
					self.changeText(self.wvar["ViewContext"],r[2])
					self.changeText(self.wvar["ViewSource"],r[3])
					pageVar.set(str(int(pp[0])+1)+" / "+pp[1])
					self.context_id = r[0]
		def prevPage():
			nonlocal pageVar
			pp = pageVar.get().split(" / ")
			if int(pp[0]) > 1:
				self.c.execute("SELECT * FROM contexts WHERE word_id=? ORDER BY id LIMIT ?,1", (self.word_id,int(pp[0])-2))
				r = self.c.fetchone()
				if r is None or r[2] is None:
					r = list(r)
					r[2] = ""
				self.changeText(self.wvar["ViewContext"],r[2])
				self.changeText(self.wvar["ViewSource"],r[3])
				pageVar.set(str(int(pp[0])-1)+" / "+pp[1])
				self.context_id = r[0]
		tk.Button(pageFrame, text="<-", command=prevPage).grid(row=0,column=0)
		self.wvar["ViewPage"] = pageVar
		tk.Label(pageFrame, textvariable=pageVar).grid(row=0,column=1)
		tk.Button(pageFrame, text="->", command=nextPage).grid(row=0,column=2)
	def editWordGui(self):
		def cancel():
			self.c.execute("SELECT word FROM words WHERE id=?", (self.word_id,))
			r = self.c.fetchone()
			if r is None or r[0] is None:
				self.c.execute("DELETE FROM words WHERE id=?", (self.word_id,))
				self.word_id = self.wvar["prevWord"]
				self.c.execute("SELECT * FROM contexts WHERE word_id=? ORDER BY id LIMIT 1", (self.word_id,))
				row = self.c.fetchone()
				if row is not None:
					self.changeText(self.wvar["ViewContext"],row[2])
					self.changeText(self.wvar["ViewSource"],row[3])
					self.context_id = row[0]
				else:
					self.changeText(self.wvar["ViewContext"],"")
					self.changeText(self.wvar["ViewSource"],"")
					self.context_id = ()
				self.c.execute("SELECT count(*) FROM contexts WHERE word_id=?", (self.word_id,))
				self.wvar["pageVar"].set("1 / "+str(self.c.fetchone()[0]))
			self.switchLayout(self.layouts,"ViewWord")
		layout = tk.Frame(self.root)
		self.layouts["EditWord"] = layout
		tk.Button(layout, text="Submit", command=self.editWord).grid(row=0,column=0)
		tk.Button(layout, text="Cancel", command=cancel).grid(row=0,column=1)
		tk.Label(layout, text="Word").grid(row=1,column=0)
		tk.Label(layout, text="Part of Speech").grid(row=2,column=0)
		tk.Label(layout, text="Gloss Word").grid(row=3,column=0)
		tk.Entry(layout, textvariable=self.wvar["ViewWord"]).grid(row=1,column=1)
		tk.Entry(layout, textvariable=self.wvar["ViewSpeech"]).grid(row=2,column=1)
		tk.Entry(layout, textvariable=self.wvar["ViewGloss"]).grid(row=3,column=1)
		translationText = ScrolledText(layout, height=8, width=80)
		self.wvar["EditWordTranslationText"] = translationText
		translationText.grid(row=4,column=0,columnspan=2)
	def editContextGui(self):
		def cancel():
			self.c.execute("SELECT context FROM contexts WHERE id=?", (self.context_id,))
			r = self.c.fetchone()
			if len(r) > 0 or r[0] is None:
				self.c.execute("DELETE FROM contexts WHERE id=?", (self.word_id,))
				self.c.execute("SELECT * FROM contexts WHERE word_id=? ORDER BY id LIMIT 1", (self.word_id,))
				r = self.c.fetchone()
				if r is not None:
					self.changeText(self.wvar["ViewContext"],r[2])
					self.context_id = r[0]
					self.c.execute("SELECT count(*) FROM contexts WHERE word_id=?", (self.word_id,))
					pageVar.set("1 / "+str(self.c.fetchone()[0]))
				else:
					self.changeText(self.wvar["ViewContext"],"")
					self.context_id = ()
					pageVar.set("1 / 0")
			self.switchLayout(self.layouts,"ViewWord")
		layout = tk.Frame(self.root)
		self.layouts["EditContext"] = layout
		tk.Button(layout, text="Submit", command=self.editContext).grid(row=0,column=0)
		tk.Button(layout, text="Cancel", command=cancel).grid(row=0,column=1)
		tk.Label(layout, textvariable=self.wvar["ViewWord"]).grid(row=1,column=0)
		tk.Label(layout, textvariable=self.wvar["ViewSpeech"]).grid(row=1,column=1)
		translationText = ScrolledText(layout, height=5, width=80)
		translationText.grid(row=2,column=0,columnspan=2)
		translationText.config(state=tk.DISABLED)
		self.wvar["EditContextTranslationText"] = translationText
		self.wvar["EditContext"] = ScrolledText(layout, height=5, width=80)
		self.wvar["EditContext"].grid(row=2,column=0,columnspan=2)
		self.wvar["EditSource"] = ScrolledText(layout, height=5, width=80)
		self.wvar["EditSource"].grid(row=3,column=0,columnspan=2)
	def editReplaceGui(self):
		layout = tk.Frame(self.root)
		self.layouts["EditReplace"] = layout
		replaceEntries = []
		replaceVars = []
		pageVar = tk.StringVar()
		pageVar.set("0 / 0")
		def returnViewWord():
			self.switchLayout(self.layouts,"ViewWord")
		def nextPage():
			nonlocal pageVar
			pp = pageVar.get().split(" / ")
			if int(pp[0]) < int(pp[1]):
				pageVar.set(str(int(pp[0])+1)+" / "+pp[1])
				self.enterReplacePage(int(pp[0])+1)
		def prevPage():
			nonlocal pageVar
			pp = pageVar.get().split(" / ")
			if int(pp[0]) > 0:
				pageVar.set(str(int(pp[0])-1)+" / "+pp[1])
				self.enterReplacePage(int(pp[0])-1)
		def submitPushed():
			nonlocal pageVar
			p = int(pageVar.get().split(" / ")[0])
			self.editReplace(p)
		tk.Button(layout, text="Submit", command=submitPushed).grid(row=0,column=0)
		tk.Button(layout, text="Return", command=returnViewWord).grid(row=0,column=1)
		pageFrame = tk.Frame(layout)
		tk.Button(pageFrame, text="<-", command=prevPage).grid(row=0,column=0)
		tk.Label(pageFrame, textvariable=pageVar).grid(row=0,column=1)
		tk.Button(pageFrame, text="->", command=nextPage).grid(row=0,column=2)
		pageFrame.grid(row=1,column=0,columnspan=2)
		for i in range(15):
			replaceVars.append((tk.StringVar(),tk.StringVar()))
			replaceEntries.append((tk.Entry(layout, textvariable=replaceVars[-1][0]),tk.Entry(layout, textvariable=replaceVars[-1][1])))
			replaceEntries[-1][0].grid(row=i+2,column=0)
			replaceEntries[-1][1].grid(row=i+2,column=1)
		self.wvar["ReplaceVars"] = replaceVars
		self.wvar["ReplacePage"] = pageVar
	def enterReplacePage(self,p):
		replaceVars = self.wvar["ReplaceVars"]
		if p > 0:
			l = sorted(self.replaceTexts.keys())[15*(p-1):15*p]
			for i in range(min(len(l),15)):
				replaceVars[i][0].set(l[i])
				replaceVars[i][1].set(self.replaceTexts[l[i]])
			for i in range(len(l),15,1):
				replaceVars[i][0].set("")
				replaceVars[i][1].set("")
		elif p == 0:
			for i in range(15):
				replaceVars[i][0].set("")
				replaceVars[i][1].set("")
	def startEditReplace(self):
		self.enterReplacePage(1)
		self.wvar["ReplacePage"].set("1 / "+str(len(self.replaceTexts)//15+1))
		self.switchLayout(self.layouts,"EditReplace")
	def addReplace(self):
		self.enterReplacePage(0)
		self.wvar["ReplacePage"].set("0 / "+str(len(self.replaceTexts)))
		self.switchLayout(self.layouts,"EditReplace")
	def editReplace(self,p):
		l = sorted(self.replaceTexts.keys())[15*(p-1):15*p]
		replaceVars = self.wvar["ReplaceVars"]
		to_delete = []
		to_update = []
		to_insert = []
		for i in l:
			if i != "" and (i not in [j[0].get() for j in replaceVars]):
				to_delete.append(i)
		for i in range(len(replaceVars)):
			if replaceVars[i][0].get() != "":
				if replaceVars[i][0].get() in self.replaceTexts.keys() and self.replaceTexts[replaceVars[i][0].get()] != replaceVars[i][1].get():
					to_update.append((replaceVars[i][0].get(),replaceVars[i][1].get()))
				elif replaceVars[i][0].get() not in self.replaceTexts.keys():
					to_insert.append((replaceVars[i][0].get(),replaceVars[i][1].get()))
		for i in to_delete:
			self.c.execute("DELETE FROM replace WHERE to_replace=?", (i,))
			del self.replaceTexts[i]
		for i in to_update:
			self.c.execute("UPDATE replace SET replace_with=? WHERE to_replace=? AND language_id=?", (i[1],i[0],self.language))
			self.replaceTexts[i[0]] = i[1]
		for i in to_insert:
			self.c.execute("INSERT INTO replace (language_id,to_replace,replace_with) VALUES (?,?,?)", (self.language,i[0],i[1]))
			self.replaceTexts[i[0]] = i[1]
		self.conn.commit()
		self.enterReplacePage(p)
	def startEditContext(self):
		self.c.execute("SELECT translation FROM words WHERE id=?", (self.word_id,))
		row = self.c.fetchone()
		self.changeText(self.wvar["EditContextTranslationText"],row[0])
		self.c.execute("SELECT context,source FROM contexts WHERE id=?", (self.context_id,))
		row = self.c.fetchone()
		self.wvar["EditContext"].delete("1.0","end")
		if row[0] is not None: self.wvar["EditContext"].insert("1.0",row[0])
		self.wvar["EditSource"].delete("1.0","end")
		if row[1] is not None: self.wvar["EditSource"].insert("1.0",row[1])
		self.switchLayout(self.layouts,"EditContext")
	def addContext(self):
		self.c.execute("INSERT INTO contexts (word_id) VALUES (?)", (self.word_id,))
		self.context_id = self.c.lastrowid
		self.conn.commit()
		pp = self.wvar["pageVar"].get().split(" / ")
		self.wvar["pageVar"].set(str(int(pp[1])+1)+" / "+str(int(pp[1])+1))
		self.startEditContext()
		self.switchLayout(self.layouts,"EditContext")
	def editContext(self):
		contextText = self.replaceString(self.wvar["EditContext"].get("1.0","end-1c"))
		sourceText = self.replaceString(self.wvar["EditSource"].get("1.0","end-1c"))
		self.c.execute("UPDATE contexts SET context=?, source=? WHERE id=?", (contextText,sourceText,self.context_id))
		self.conn.commit()
		self.changeText(self.wvar["ViewContext"],contextText)
		self.changeText(self.wvar["ViewSource"],sourceText)
		self.switchLayout(self.layouts, "ViewWord")
	def startEditWord(self):
		self.c.execute("SELECT translation FROM words WHERE id=?", (self.word_id,))
		row = self.c.fetchone()
		self.wvar["EditWordTranslationText"].delete("1.0","end")
		self.wvar["EditWordTranslationText"].insert("1.0",row[0])
		self.switchLayout(self.layouts,"EditWord")
	def addWord(self):
		self.c.execute("INSERT INTO words (language_id) VALUES (?)", (self.language,))
		self.wvar["prevWord"] = self.word_id
		self.word_id = self.c.lastrowid
		self.wvar["EditWordTranslationText"].delete("1.0","end")
		self.wvar["ViewWord"].set("")
		self.wvar["ViewSpeech"].set("")
		self.wvar["ViewGloss"].set("")
		self.switchLayout(self.layouts,"EditWord")
	def editWord(self):
		if self.wvar["prevWord"] is not None and self.wvar["prevWord"] != self.word_id:
			self.wvar["prevWord"] = None
			self.changeText(self.wvar["ViewContext"],"")
			self.changeText(self.wvar["ViewSource"],"")
			self.context_id = ()
		wordText = self.replaceString(self.wvar["ViewWord"].get())
		translationText = self.replaceString(self.wvar["EditWordTranslationText"].get("1.0","end-1c"))
		speechText = self.replaceString(self.wvar["ViewSpeech"].get())
		glossText = self.replaceString(self.wvar["ViewGloss"].get())
		self.c.execute("SELECT * FROM words WHERE id=?", (self.word_id,))
		row = self.c.fetchone()
		if row[2] != wordText:
			self.c.execute("UPDATE words SET word=? WHERE id=?", (wordText,self.word_id))
		self.c.execute("UPDATE words SET translation=? WHERE id=?", (translationText,self.word_id))
		self.c.execute("SELECT id FROM speech_categories WHERE name=?", (speechText,))
		row = self.c.fetchone()
		if row is None:
			self.c.execute("INSERT INTO speech_categories (name) VALUES (?)", (speechText,))
			self.c.execute("UPDATE words SET speech_category=? WHERE id=?", (self.c.lastrowid,self.word_id))
			row = (self.c.lastrowid,)
		else:
			self.c.execute("UPDATE words SET speech_category=? WHERE id=?", (row[0],self.word_id))
		self.c.execute("SELECT * FROM words WHERE word=? AND speech_category=? AND gloss=? AND language_id=?", (wordText,row[0],glossText,self.language))
		rows = self.c.fetchall()
		if glossText != "" and (len(rows) >= 2 or (len(rows) == 1 and rows[0][0] != self.word_id)):
			self.popmsg("Gloss word duplicate and not updated","Error")
		else:
			self.c.execute("UPDATE words SET gloss=? WHERE id=?", (glossText,self.word_id))
		self.conn.commit()
		self.changeText(self.wvar["ViewTranslation"],translationText)
		self.wvar["ViewWord"].set(wordText)
		self.wvar["ViewSpeech"].set(speechText)
		self.wvar["ViewGloss"].set(glossText)
		self.switchLayout(self.layouts,"ViewWord")
	def useLanguage(self,langID):
		self.language = langID
		self.word_id = ()
		self.context_id = ()
		self.replaceTexts = {}
		self.c.execute("SELECT name FROM languages WHERE id=?", (langID,))
		langName = self.c.fetchone()[0]
		self.c.execute("SELECT * FROM replace WHERE language_id=?", (langID,))
		for i in self.c.fetchall():
			self.replaceTexts[i[1]] = i[2]
		self.switchLayout(self.layouts,"ViewWord")
		self.menubar.entryconfig("Options",state="normal")
	def searchWord(self,word):
		wordReplace = self.replaceString(word)
		def radioSelected():
			id = self.wvar["SelectWordVar"].get()
			self.c.execute("SELECT * FROM words w INNER JOIN speech_categories s ON w.speech_category=s.id WHERE w.id=?", (id,))
			row = self.c.fetchone()
			self.wvar["ViewWord"].set(row[2])
			self.wvar["ViewSpeech"].set(row[-1])
			self.wvar["ViewGloss"].set(row[5])
			self.changeText(self.wvar["ViewTranslation"],row[3])
			self.c.execute("SELECT * FROM contexts WHERE word_id=? ORDER BY id LIMIT 1", (id,))
			row = self.c.fetchone()
			if row is not None:
				self.changeText(self.wvar["ViewContext"],row[2])
				self.changeText(self.wvar["ViewSource"],row[3])
				self.context_id = row[0]
			else:
				self.changeText(self.wvar["ViewContext"],"")
				self.changeText(self.wvar["ViewSource"],"")
			self.c.execute("SELECT count(*) FROM contexts WHERE word_id=?", (id,))
			self.wvar["pageVar"].set("1 / "+str(self.c.fetchone()[0]))
			self.word_id = id
		self.c.execute("SELECT w.id,w.word,s.name,w.gloss FROM words w INNER JOIN speech_categories s ON w.speech_category=s.id WHERE w.language_id=? AND w.word LIKE ?", (self.language,wordReplace))
		r = self.c.fetchall()
		for i in range(min(len(r),len(self.wvar["SelectWordRadio"]))):
			glossText = ""
			if r[i][3] is not None and r[i][3] != "":
				glossText = " ("+r[i][3]+") "
			self.wvar["SelectWordRadio"][i].config(text=r[i][1]+glossText+", "+r[i][2],value=r[i][0])
		if len(r) < len(self.wvar["SelectWordRadio"]):
			for i in range(len(r),len(self.wvar["SelectWordRadio"]),1):
				self.wvar["SelectWordRadio"][i].grid_forget()
			del self.wvar["SelectWordRadio"][len(r):]
		elif len(r) > len(self.wvar["SelectWordRadio"]):
			for i in range(len(self.wvar["SelectWordRadio"]),len(r),1):
				glossText = ""
				if r[i][3] is not None and r[i][3] != "":
					glossText = " ("+r[i][3]+") "
				newRadio = tk.Radiobutton(self.wvar["SelectWordFrame"],text=r[i][1]+glossText+", "+r[i][2],value=r[i][0],variable=self.wvar["SelectWordVar"],command=radioSelected)
				newRadio.grid(row=len(self.wvar["SelectWordRadio"])//5, column=len(self.wvar["SelectWordRadio"])%5)
				self.wvar["SelectWordRadio"].append(newRadio)
	def switchLayout(self,layoutDict,layoutKey):
		if layoutKey in layoutDict:
			if "active" in layoutDict:
				layoutDict["active"].grid_forget()
			layoutDict[layoutKey].grid()
			layoutDict["active"] = layoutDict[layoutKey]
			return True
		else:
			return False
	def replaceString(self,t):
		for i in self.replaceTexts:
			for i in self.replaceTexts.keys():
				t = t.replace(i,self.replaceTexts[i])
		return t
	@staticmethod
	def changeText(textWgt,newText):
		textWgt.config(state=tk.NORMAL)
		textWgt.delete("1.0","end")
		textWgt.insert("1.0",newText)
		textWgt.config(state=tk.DISABLED)
	@staticmethod
	def popmsg(text,title=""):
		popup = tk.Toplevel()
		popup.wm_title(title)
		tk.Label(popup,text=text).grid(row=0,column=0)
		tk.Button(popup,text="OK",command=popup.destroy).grid(row=1,column=0)

LanguageNotes()
