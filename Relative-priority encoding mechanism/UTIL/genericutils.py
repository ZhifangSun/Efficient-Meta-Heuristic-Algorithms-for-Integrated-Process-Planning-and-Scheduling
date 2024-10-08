#!/usr/bin/env python3
# *-* coding:utf8 *-*

"""
类别: 工具组件
名称: 通用工具
作者: strong
邮件: jqjiang@hnist.edu.cn
日期: 2020年3月20日
"""

from COMPONENT.message import Message
from COMPONENT.task import Task
from xml.dom import minidom
from CONFIG.config import *
import numpy


# 打印列表函数
def print_list(object_list):
    for o in object_list:
        print(o)


# 计算调度序列完工时间函数
def calculate_makespan(scheduling_list):
    makespan = 0.0
    for task in scheduling_list.list.keys():
        if task.is_exit:
            finish_time = task.assignment.running_span.finish_time
            makespan = finish_time if finish_time > makespan else makespan
    scheduling_list.makespan = makespan
    return makespan


# 计算调度序列总成本函数
def calculate_cost(scheduling_list):
    cost = 0.0
    for task in scheduling_list.list.keys():
        assigned_processor = task.assignment.assigned_processor
        cst = task.processor__computation_cost[assigned_processor]
        cost += cst
    scheduling_list.cost = cost
    return cost

def runningEnergyInVRF(task,processor,vrf):
    maxVRF = processor.vrfs[0][0]
    e=0
    if task.isVirtual:
        e=0.0
    else:
        # print(maxVRF.frequency,vrf.frequency)
        e=pow(vrf.voltage,2)*vrf.frequency*(task.processor__computation_time[processor]*maxVRF.frequency/vrf.frequency)
    return e

def consumeEnergyInVRF(processors,scheduling_list,makespan):
    runningE=0.00
    for task in scheduling_list.list.keys():
        assigned_processor = task.assignment.assigned_processor
        vrf = task.assignment.vrf
        # print(vrf.voltage,vrf.frequency)
        runningE += runningEnergyInVRF(task, assigned_processor, vrf)

    idleE=idleEnergyInVRF(processors, scheduling_list)
    allE=runningE + idleE
    return allE

def idleEnergyInVRF(processors,scheduling_list):
    energy = 0.00
    for p in processors:
        sumMS = 0.00
        Vrfs=p.vrfs[0]
        lowestV=Vrfs[len(Vrfs)-1].voltage
        lowestF=Vrfs[len(Vrfs)-1].frequency
        # print(lowestV,lowestF)
        residentTasks=p.resident_tasks
        if len(residentTasks)>0:
            makespan=residentTasks[len(residentTasks)-1].makespan_ft
        for t in scheduling_list.list.keys():
            assignedProcessor=t.processor
            if p==assignedProcessor:
                st=p.getTask_RunningTimeMap[t].start_time
                ft=p.getTask_RunningTimeMap[t].finish_time
                print(st,ft)
                ms=ft-st
                sumMS=sumMS+ms
        idleTime=makespan-sumMS
        print(idleTime,sumMS)
        eachE=pow(lowestV,2)*lowestF*idleTime
        energy=energy+eachE

    return energy



# 打印调度序列
def print_scheduling_list(scheduling_list):
    for task in scheduling_list.list.keys():
        info = "%s on %s with %s" % (task, task.assignment.assigned_processor, task.assignment.running_span)
        print(info)



def readfile(XmlFile):
    doc = minidom.parse(XmlFile)
    root=doc.getElementsByTagName("adag")
    tasknum=int(root[0].getAttribute("jobCount"))
    computation_time_matrix=numpy.full((tasknum,6),float("inf"))
    communication_time_matrix=numpy.full((tasknum,tasknum),float("inf"))
    job=root[0].getElementsByTagName("job")
    for child in root[0].getElementsByTagName("child"):
        ch=int(child.getAttribute("ref")[2:])
        for parent in child.getElementsByTagName("parent"):
            pa = int(parent.getAttribute("ref")[2:])
            for uses in reversed(job[pa].getElementsByTagName("uses")):
                if uses.getAttribute("link")=="output":
                    for use in job[ch].getElementsByTagName("uses"):
                        if use.getAttribute("link")=="input" and uses.getAttribute("file")==use.getAttribute("file"):
                            communication_time_matrix[pa][ch]=abs(float(use.getAttribute("size")))/(2*1048576)
                            break
                else:
                    break

    for job in root[0].getElementsByTagName("job"):
        id=int(job.getAttribute("id")[2:])
        length=max(abs(float(job.getAttribute("runtime"))),0.001)
        pc=[1,1,2,2,3,3]
        for p in range(6):
            computation_time_matrix[id][p]=round(length/pc[p],2)
    computation_time_matrix=computation_time_matrix.tolist()
    communication_time_matrix=communication_time_matrix.tolist()
    return computation_time_matrix,communication_time_matrix


def final_matrix(a, b, c, d, e):
    computation_time_matrix=[]
    communication_time_matrix=[]
    not_in_OR=[]
    OR= {}
    OR_in= {}


    temp=[]
    for i in a:
        computation_time_matrix=computation_time_matrix+i


    task_number=0
    task_number_list=[]
    for i in b:
        task_number+=len(i)
        task_number_list.append(task_number)
    task_number_list1=[0]+task_number_list

    OR_number=0
    OR_number_list=[]
    for i in d:
        OR_number+=len(i)
        OR_number_list.append(OR_number)
    OR_number_list1=[0]+OR_number_list
    # print("qwert")
    # print(OR_number_list1)
    # print(OR_number)
    for j in range(len(b)):
        for l in b[j]:
            temp=[]
            for p in range(task_number_list1[j]):
                temp.append(INF)
            temp+=l
            for q in range(task_number_list1[j+1],task_number):
                temp.append(INF)
            communication_time_matrix.append(temp)


    for i in range(len(c)):
        for j in c[i]:
            not_in_OR.append(j+task_number_list1[i])


    for i in range(len(d)):
        for k,v in d[i].items():
            dic1 = tuple()
            dic2 = tuple()
            for l in k:
                dic1 = dic1+(l+task_number_list1[i],)
            for r in v:
                dic2 = dic2 + (r+task_number_list1[i],)
            OR[dic1]=dic2


    for i in range(len(e)):
        for k,v in e[i].items():
            l=k+OR_number_list1[i]
            tup=(v[0]+OR_number_list1[i],v[1])
            OR_in[l]=tup


    return computation_time_matrix, communication_time_matrix, not_in_OR, OR, OR_in