import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import math
import io
import datetime

st.set_page_config(page_title="Planning de Morgane", page_icon="🍣", layout="wide", initial_sidebar_state ="auto")

def convertHourToString(stringifiedHour):
    time = float(stringifiedHour)
    hour = str(math.floor(time))
    minutes = int(round((time % 1) * 60))

    if minutes == 0:
        return hour + "h"

    return hour + "h" + str(minutes)

def substractHours(hour1, hour2):
    return hour2 - hour1

def convertHourTupleToString(stringifiedHourTuple):
    return convertHourToString(str(stringifiedHourTuple[0])) + " - " + convertHourToString(str(stringifiedHourTuple[1]))

def isPersonWorking(startDate, endDate, personnalArray):
    for shift in personnalArray:
        if startDate >= shift[0] and endDate <= shift[1]:
            return True
    return False

def findNumberOfPersonsWorking(startDate, endDate, data):
    count = 0
    for personnalArray in data:
        if isPersonWorking(startDate, endDate, personnalArray):
            count += 1
    return count

def plot_event(ax, A, i, **kwargs):
    segs = [[(x, i), (y, i)] for (x, y) in A]
    line_segments = LineCollection(segs, lw=8, **kwargs)
    ax.add_collection(line_segments)

def generatePlotXTicksAndLabels(data):
    plotXTicks = set([])
    for personnalArray in data:
        for hours in personnalArray:
            plotXTicks.add(hours[0])
            plotXTicks.add(hours[1])
    plotXTicks = list(plotXTicks)
    plotXTicks.sort()

    plotXLabelsTemp = [str(i) for i in plotXTicks]
    plotXLabels = []
    i = 0
    for stringifiedHour in plotXLabelsTemp:
        i += 1
        tempString = convertHourToString(stringifiedHour)
        if (i%2 == 0):
            tempString = "\n" + tempString
        plotXLabels.append(tempString)

    return plotXTicks, plotXLabels

def getGraphTitle(weekDay):
    prefix = (graphTitle + ' - ') if len(graphTitle) > 0 else ''
    return prefix + weekDay

def displayOneGraph(weekDay):
    planning = st.session_state.tkinterData[weekDay]
    title = getGraphTitle(weekDay)

    names = []
    data = []

    for name, personnalPlanning in planning.items():
        names.append(name)
        data.append(personnalPlanning)

    fig, ax = plt.subplots(1,1, figsize=(18,13))

    displayGraph(ax, data, names, title)

    return fig



def displayGraph(ax, data, names, title):

    numberOfPersons = len(data)
    numberOfColors = len(colors)
    ymax = numberOfPersons * 20
    heights = [20*i + 10 for i in range(numberOfPersons)]
    plotXTicks, plotXLabels = generatePlotXTicksAndLabels(data)


    for hour in plotXTicks:
        ax.axvline(x = hour, color = 'black')

    for j, (i, event) in enumerate(zip(heights, data)):
        workingDuration = 0
        for segment in event:
            workingDuration += substractHours(segment[0], segment[1])
        plot_event(ax, event, i, color=colors[j%numberOfColors])
        plt.text(6, i, names[j], color=colors[j%numberOfColors], fontsize=12, va='center', ha='center')
        plt.text(20 , i, convertHourToString(workingDuration), color=colors[j%numberOfColors], fontsize=12, va='center', ha='center')

    for index in range(len(plotXTicks)-1):
        startDate = plotXTicks[index]
        endDate = plotXTicks[index+1]
        numberOfPersonsWorking = findNumberOfPersonsWorking(startDate, endDate, data)
        xDisplayPoint = (startDate + endDate)/2
        plt.text(xDisplayPoint, -15, str(numberOfPersonsWorking), fontsize=15, color='black', horizontalalignment='center')

    ax.set_xlim(7, 19)
    ax.set_xticks(plotXTicks)
    ax.set_xticklabels(plotXLabels)
    ax.set_ylim(-30, ymax)
    ax.get_yaxis().set_visible(False)
    ax.set_title(title)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.plot(1, -30, ">k", transform=ax.get_yaxis_transform(), clip_on=False)


colors = [
    'tab:blue',
    'tab:red',
    'tab:green',
    'tab:orange',
    'tab:gray',
    'tab:purple',
    'tab:olive',
    'tab:brown',
    'tab:pink',
    'tab:cyan',
]

if "tkinterData" not in st.session_state:
    st.session_state.tkinterData = {
        'Lundi': {},
        'Mardi': {},
        'Mercredi': {},
        'Jeudi': {},
        'Vendredi': {},
    }

weekDaysOptions = [
    'Lundi',
    'Mardi',
    'Mercredi',
    'Jeudi',
    'Vendredi',
    'Toute la semaine',
]

def transformDictToString(tkinterData, weekDay):
    returnedString = weekDay + " :   \n"
    if len(tkinterData[weekDay].items()) == 0:
        returnedString += "        personne  \n"
    for personName, personnalPlanning in tkinterData[weekDay].items():
        returnedString += "        "
        returnedString += str(personName)
        returnedString += " : "
        returnedString += " et ".join(map(convertHourTupleToString, personnalPlanning))
        returnedString += "  \n"
    return returnedString

def transformFullDictToString(tkinterData):
    fullText = ""
    for weekday in weekDaysOptions[:5]:
        fullText += transformDictToString(tkinterData, weekday)
    return fullText

def updateData(weekDay, dataToAdd, name):
    planning = st.session_state.tkinterData[weekDay]

    if name in planning:
        planning[name].append(dataToAdd)
    else:
        planning[name] = [dataToAdd]

def removeData(weekDay, name):
    planning = st.session_state.tkinterData[weekDay]
    if name in planning:
            del planning[name]

with st.sidebar:
    userToUpdate = st.text_input('Nom de la personne à ajouter')
    startTime = st.time_input('Horaire de début', value=datetime.time(8, 00))
    endTime = st.time_input('Horaire de fin', value=datetime.time(18, 00))
    addTimeWeekDay = st.selectbox("Jour d'ajout", weekDaysOptions, index=5)

    if st.button("Ajouter les horaires au planning"):
        startHour = startTime.hour
        startMinutes = startTime.minute
        endHour = endTime.hour
        endMinutes = endTime.minute

        startDate = float(startHour + (startMinutes / 60))
        endDate = float(endHour + (endMinutes / 60))
        dataToAdd = (float(startDate), float(endDate))

        if (addTimeWeekDay != weekDaysOptions[5]):
            updateData(addTimeWeekDay, dataToAdd, userToUpdate)
        else:
            for existingWeekDay in weekDaysOptions[:5]:
                updateData(existingWeekDay, dataToAdd, userToUpdate)

    st.divider()

    userToDelete = st.text_input('Nom de la personne à retirer')
    deleteUserWeekDay = st.selectbox('Jour de retrait', weekDaysOptions, index=5)

    if st.button("Supprimer une personne du planning"):
        if (deleteUserWeekDay != weekDaysOptions[5]):
            removeData(deleteUserWeekDay, userToDelete)
        else:
            for existingWeekDay in weekDaysOptions[:5]:
                removeData(existingWeekDay, userToDelete)

column1, column2 = st.columns([2, 1], gap="large")

column2.text(transformFullDictToString(st.session_state.tkinterData))

downloadWeekDay = column1.selectbox('Pour quel jour voulez-vous télécharger un graphique ?', weekDaysOptions[:5])
graphTitle = column1.text_input('Voulez vous rajouter un titre au graphique ?')

fig = displayOneGraph(downloadWeekDay)
column1.pyplot(fig)

fileName = getGraphTitle(downloadWeekDay)
image = io.BytesIO()
fig.savefig(image, format='png')

btn = column1.download_button(
   label="Télécharger le graphique",
   data=image,
   file_name=f"{fileName}.png",
   mime="image/png",
   type="primary"
)