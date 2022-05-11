import PySimpleGUI as sg
from arcade import Scene
import numpy as np
import time

sg.theme('LightGrey2')

remain=0
running=None
def mark(e,findtile,arr,scene):
    r,c= findtile.get(e.widget)
    if arr[r][c] & 32:return
    if arr[r][c] & 64:
        scene[f'g{str(r)}.{str(c)}'].update(text=' ')
    else:
        scene[f'g{str(r)}.{str(c)}'].update(text='⚑')
    arr[r][c]^=64

# uint8位数据，128为是不是雷，64为是否插旗，32为是否翻开
def genborad(row,col,mine):
    l=(row*col-mine)*[0]+[128]*mine
    arr=np.array(l,dtype=np.uint8)
    np.random.shuffle(arr)
    arr=np.reshape(arr,(row,col))
    for r in range(row):
        for c in range(col):
            if arr[r][c]&128:
                for nr in range(max(r-1,0),min(r+2,len(arr))):
                    for nc in range(max(c-1,0),min(c+2,len(arr))):
                        arr[nr][nc]+=1
    print(arr)
    return arr

def revblock(r,c,arr,w,h,scene):
    global remain
    for nr,nc in [(r,c),(r-1,c),(r+1,c),(r,c+1),(r,c-1),(r-1,c-1),(r-1,c+1),(r+1,c+1),(r+1,c-1)]:
        if nr in range(h) and nc in range(w) and arr[nr][nc] & 32==0:
            if arr[nr][nc]==0:
                remain-=1
                scene[f'g{str(nr)}.{str(nc)}'].Widget.config(relief='sunken', overrelief='')
                arr[nr][nc]|=32
                revblock(nr,nc,arr,w,h,scene)
            elif arr[nr][nc] & 128==0:
                scene[f'g{str(nr)}.{str(nc)}'].Widget.config(relief='sunken', overrelief='')
                scene[f'g{str(nr)}.{str(nc)}'].update(text=str(arr[nr][nc] & 15))
                arr[nr][nc]|=32
                remain-=1


def reveal(r,c,arr,w,h,scene):
    global remain,running,starttime
    if not running:
        running=time.time()
    if arr[r][c] & 64:
        return 0
    elif arr[r][c]&128:
        scene[f'g{str(r)}.{str(c)}'].update(button_color='red')
        for row in range(h):
            for col in range(w):
                if arr[row][col] & 64: # 有标旗子
                    if arr[row][col]& 128==0:  # 并不是地雷
                        scene[f'g{str(r)}.{str(c)}'].update(button_color='red')  # 红色显示
                elif arr[row][col] & 128:  # 是地雷
                    scene[f'g{str(row)}.{str(col)}'].update(text='☀')  # 显示为地雷
                elif arr[row][col] & 15>0:
                    scene[f'g{str(row)}.{str(col)}'].update(text=str(arr[row][col] & 15))
                    scene[f'g{str(row)}.{str(col)}'].Widget.config(relief='sunken', overrelief='')
                else:
                    scene[f'g{str(row)}.{str(col)}'].Widget.config(relief='sunken', overrelief='')
        sg.Window('游戏失败',[[sg.Text('非常不幸，触雷失败')],[sg.Push(),sg.Button('确定'),sg.Push()]]).read(close=True,timeout=5000)
        scene.TKroot.after_cancel(running)
        running=None
        return 0
    elif arr[r][c] & 32:    # 点击已经翻开的格子
        num=arr[r][c] & 15  # 取出当前格的数字
        for nr in range(max(r-1,0),min(r+2,len(arr))):
            for nc in range(max(c-1,0),min(c+2,len(arr))):
                if arr[nr][nc] & 64: # 如果已经标旗子
                    num-=1
        if num==0:  # 已标旗数与数字吻合，模拟点击其它格子
            for nr in range(max(r-1,0),min(r+2,len(arr))):
                for nc in range(max(c-1,0),min(c+2,len(arr))):
                    if arr[nr][nc] & 32==0:
                        reveal(nr,nc,arr,w,h,scene)

    elif arr[r][c]>0:
        arr[r][c] |= 32  # 表示翻开
        scene[f'g{str(r)}.{str(c)}'].Widget.config(relief='sunken', overrelief='')
        scene[f'g{str(r)}.{str(c)}'].update(text=str(arr[r][c] & 15))
        remain-=1
    else:
        revblock(r,c,arr,w,h,scene)

def resstart(w,h,m,s):
    board=genborad(w,h,m)
    for r in range(h):
        for c in range(w):
            s[f'g{str(r)}.{str(c)}'].update(text=" ")
            s[f'g{str(r)}.{str(c)}'].update(button_color='lightgrey')
            s[f'g{str(r)}.{str(c)}'].Widget.config(relief='raised', overrelief='flat')
    return board


def Main(w,h,m):
    board=genborad(w,h,m)
    findtile={}
    global remain,running
    remain=w*h-m
    ground=[[sg.Button(" ",size=(2,1),pad=0,key=f'g{str(r)}.{str(c)}') for r in range(h)] for c in range(w)]     
    view=[[sg.Text("计时："),sg.Text("0",key='time'),sg.Push(),sg.T("剩余"),sg.T(remain,key='remain')],ground,[sg.T("宽"),sg.In(s=3,key='width'),sg.Push(),sg.T("高"),sg.In(s=3,key='height'),sg.Push(),sg.T("雷"),sg.In(s=3,key='mine'),sg.Push(),sg.B('开始',key='reset',focus=True)]]
    scene=sg.Window("扫雷",layout=view,finalize=True)
    scene['width'](w)
    scene['height'](h)
    scene['mine'](m)
    for r in range(h):
        for c in range(w):
            scene[f'g{str(r)}.{str(c)}'].Widget.config(relief='raised', overrelief='flat')
            scene[f'g{str(r)}.{str(c)}'].Widget.bind('<Button-3>', lambda e: mark(e,findtile,board,scene))
            findtile[scene[f'g{str(r)}.{str(c)}'].Widget]=(r,c)    
    while True:
        event,vals=scene.read(500)
        print(event, vals) if event!="__TIMEOUT__" else None
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        elif event.startswith('g'):
            r,c=(int(i) for i in event[1:].split("."))
            reveal(r,c,board,w,h,scene)
            scene['remain'].update(remain)
            print(remain)
            if remain==0:
                sg.Window('游戏成功',[[sg.Text('你真厉害，成功完成')],[sg.Push(),sg.Button('确定'),sg.Push()]]).read(close=True)
                scene.TKroot.after_cancel(running)
                running=None
        elif event=="reset":
            w=int(vals['width'])
            h=int(vals['height'])
            m=int(vals['mine'])
            scene.close()
            Main(w,h,m)
        if running:
            scene['time'](round(time.time() - running))
    scene.close()


if __name__ == "__main__":
    Main(15,15,30)


