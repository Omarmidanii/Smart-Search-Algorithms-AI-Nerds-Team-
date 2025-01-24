# main.py
from Structure.State import State
from Structure.Node import Node
from Logic import Logic
import random
import numpy as np
import copy 

def main():
    logic = Logic()
    logic.Play()
    #logic.play4Humans()
    

if __name__ == "__main__":
    main()

# State Class
class State:
    def __init__(self):
        self.board = np.full(52, "" , dtype='<U8')
        self.maximum_win_depth = np.full(4 , 5)
        # for safe positions
        k = 0
        while(k <= 39):
            self.board[k] = 's'
            self.board[k + 8] = 's'
            k += 13
        
        self.piece = np.full((4 , 4) , -1)

    def update_piece_position(self , value , row, col):
        if self.check_2d_dimensions(self.piece , row , col):
            self.piece[row][col] = value 
        else:
             print(f"Index out of range for piece array in row : {row} and col : {col}")

    def check_2d_dimensions(self , list , row , col):
        return 0 <= row < len(list) and 0 <= col < len(list[row])
    
    def get_pos(self, pos):
        if(pos >= 52):
            pos = pos - 51 - 1
        return pos
    
    # Node Class
    
class Node:
    def __init__(self, playersNum=2):
        self.state = State()
        self.nextnodes=np.empty((4 , 7),dtype=Node)
        self.chance=np.full(4 , 0)      # فائدة تركيب قطعة 7  
                                        # opp_moves/2 = فائدة قتل قطعة
                                        # نتيجة خسارة قطعة = -(move + 9), فائدة دخول قطعة لمسار الفوز 25
        self.killCnt=0
        self.player=2
        self.playersNum=playersNum
        self.six_hit_counter = 0
    
    
    def Generate_Next_States(self):
        
        new_player=self.WhoIsNextPlayer()
        P_actions=self.Get_Possible_Moves(new_player)
       
        for i in P_actions:
         
            new_node=Node(self.playersNum)
               
            new_node.deepCopy(self, new_player)
            
            
            if i[1] == 6: # عم عالج عداد ال6 بحيث اذا لسا اقل من 3 بزيده و غير هيك بصفره
               if new_node.six_hit_counter<3:
                   new_node.six_hit_counter=new_node.six_hit_counter+1
               else:
                   new_node.six_hit_counter=0
            else:
                   new_node.six_hit_counter=0
                   
            
               
            curr_substr = str(new_player) + str(i[0]) # عم اخد البير يلي بيعبر عن اللاعب و القطعة تبعه يلي بدنا نضيفهم على البورد هلق
               
            if new_node.state.piece[new_player][i[0]]==-1 and i[1] == 6:    #تركيب القطعة 
                new_node.state.piece[new_player][i[0]]=new_player*13
                new_pos=new_player*13
                new_node.state.board[new_pos]=curr_substr+new_node.state.board[new_pos]   #add the piece to the new position string
                new_node.chance[new_player]+=7
                
                
                
            else:   # اذا مو تركيب قطعة منعالج حالة مسار الفوز او حركة عادية
                old_pos=new_node.state.piece[new_player][i[0]] # البوزيشن القديم قبل ما اتحرك
                curr_ind = new_node.state.board[old_pos].find(curr_substr) # عم جيب الاندكس تبعي من المصفوفة
                new_node.state.board[old_pos] = new_node.state.board[old_pos][:curr_ind] + new_node.state.board[old_pos][curr_ind+2:]  # remove the peice from the string of the old position

                win_pos = self.Is_Win_Path(new_player, old_pos, i[1]) # عم شيك اذا الحركات رح يوصلوني لمسار الفوز اما لا
                if win_pos != -1: # اذا وصلت لاعمق نقطة بمسار الفوز
                    new_node.state.piece[new_player][i[0]] = -2 # يعني اللاعب فاز
                    new_node.state.maximum_win_depth[new_player]=new_node.state.maximum_win_depth[new_player]-1 #نقصت العمق تبع مسار الفوز
                    new_node.chance[new_player]+=25 # زودنا نقاط اللاعب يلي فاز


                else:
                    new_pos=new_node.state.get_pos( old_pos+i[1]) # نجيب البوزيشن الجديد بعد الحركة
                    new_node.state.piece[new_player][i[0]] = new_pos # عم نعدل البوزيشن بالمصفوفة المساعدة
                    new_node.chance[new_player] += i[1] # عم نزيد نقاط اللاعب يلي تحرك
                    for j in range(len(new_node.state.board[new_pos])): # عم امرق عل السترينغ مشان عالج حالة القتل لكل قطعة
                        if j%2==1:
                            continue
                        if new_node.state.board[new_pos][j]!=str(new_player) and self.state.board[new_pos][-1] != 's': #kill the Opponent 
                            add =0
                            died = ord(new_node.state.board[new_pos][j])-ord('0')
                            if (died * 13 <= new_pos):
                                add = new_pos - died*13 + 1
                            else:
                                add = 52 - died*13 + new_pos
                            new_node.chance[new_player]+=add/2
                            new_node.chance[died]-=(add + 9) 
                            new_node.state.piece[ord(new_node.state.board[new_pos][j])-ord('0')][ord(new_node.state.board[new_pos][j+1])-ord('0')]=-1 #change its place in the piece array
                            new_node.state.board[new_pos]=new_node.state.board[new_pos][:j]+new_node.state.board[new_pos][j+2:] #delete it from the string in bpard array
                            new_node.killCnt=new_node.killCnt+1
                            j=j-1


                    new_node.state.board[new_pos]=curr_substr+new_node.state.board[new_pos]   #add the piece to the new position string
                    if new_node.killCnt==self.killCnt: new_node.killCnt=0
                    else:  new_node.killCnt=1
            
            self.nextnodes[i[0]][i[1]]=new_node # عم خزن الستيت يلي ولدتها
            
            if new_player!=self.player: # للحركات الغير المتاحة منخزن نفس النود و منبدل اللاعب
                for i in range(0,4):
                    for j in range(1,7):
                        if self.nextnodes[i][j]==None:
                            new_node=Node(self.playersNum)
                            new_node.deepCopy(self, new_player)
                            if j==6: new_node.six_hit_counter=new_node.six_hit_counter+1
                            self.nextnodes[i][j]=new_node
        return P_actions

    
    def Is_Wall(self, Pos , player):
        if len(self.state.board[int(Pos)]) < 4:
               return False
        cnt = np.full(4 , 0)
        wall = False
        for i,j in enumerate(self.state.board[int(Pos)]):
                if i%2 == 0 and j != 's':
                    cnt[ord(j) - ord('0')] += 1
                    if cnt[ord(j) - ord('0')] >= 2 and ord(j) - ord('0') != player :
                        wall = True
        return wall


    def Is_Win_Path(self, player, Pos , dice):
        end_pos = 0
        if(player == 0):
            end_pos = 50
        else:
            end_pos = (player) * 13 - 2
        if end_pos >= Pos and dice - (end_pos - Pos) > 0:
            return dice - (end_pos - Pos)
        return -1

    
    def Get_Possible_Moves(self , nextPlayer):
        possible_moves = [] # عم تخزن بيرات كل بير بيعبر عن رقم القطعة وعدد الخطوات يلي عم تقدر تتحركهم
        for i in range(4): # عم نمرق على القطع
          if self.state.piece[nextPlayer][i] == -1: # اذا القطعة لسا ما تركبت
              possible_moves.append((i , 6))
          elif self.state.piece[nextPlayer][i] == -2: # اذا فازت القطعة ف مافي الها ايا حركة
              continue
          else:
              for j in range(1 , 7): # عم نمرق عل الحركات 
                  pos = self.state.get_pos(self.state.piece[nextPlayer][i] + j) # لنجيب البوزيشن الجديد بعد ما طبقنا الخطوات
                  win_pos = self.Is_Win_Path(nextPlayer, self.state.piece[nextPlayer][i], j) # عم نتاكد اذا القطعة بتوصل لمسار فوز اما لا و التابع بيرجعلي كم خطوة مشيت بمسار الفوز اذا فتت و -1 اذا ما فتت
                  if self.Is_Wall(pos, nextPlayer): # عم نتاكد اذا في جدار بعد ما طبق الخطوات
                        if self.state.board[pos][-1] != 's':# اذا في جدار ف بدي اتاكد اذا هو بمنطقة امنة اما لا 
                             possible_moves.append((i , j))# اذا مو بمنطقة امنة ف بقدر وقف عل الجدار
                        break
                  elif win_pos==-1:# اذا مافي شي بالمكان الجديد يلي رايح عليه ف خلص الحركة ممكنة
                    possible_moves.append((i , j))
                  elif self.state.maximum_win_depth[nextPlayer] == win_pos: # اذا وصل لاعمق نقطة بمسار الفوز
                       possible_moves.append((i , j)) 
                    
        return possible_moves


    
    def deepCopy(self, node, new_player):
        self.player=new_player
        self.chance =copy.deepcopy(node.chance)
        self.state = copy.deepcopy(node.state)
        if new_player==node.player:
            self.killCnt=node.killCnt
            self.six_hit_counter = node.six_hit_counter
        return ""
    
    
    def Apply_Move(self, piece , moves):
        return self.nextnodes[piece][moves]


    def Is_Win(self):
        return self.state.maximum_win_depth[self.player] == 1
    
    def WhoIsNextPlayer(self):
        new_player=self.player
        if (self.six_hit_counter==0 or self.six_hit_counter==3) and self.killCnt==0 :
            new_player=(self.player +1+(self.playersNum==2)*1) % 4  #change player
        return new_player
    


    def Print_State(self):
        st = ""
        j = 0
        colores = [
            "\033[31m",
            "\033[32m",
            "\033[33m",
            "\033[34m"
        ]
        if len(self.state.board[0]) > 1:
            print("\033[31m| " , end='')
            for k in range(len(self.state.board[0])):
                if k%2 == 0 and self.state.board[j][k] != 's':
                    st += f"{colores[ord(self.state.board[j][k]) - ord('0')]}{self.state.board[j][k+1:k+2]}\033[0m"
                elif self.state.board[j][k] == 's':
                    st += f"\033[31m{"s"}\033[0m"
            num = (9 - (len(st) - (int(len(self.state.board[j])/2) + 1*(len(self.state.board[j])%2!=0))*9))
            for _ in range(num):
                st = st + " "
            print(st, end='')
            
        else:
            print(f"\033[31m| {self.state.board[j]:^9} \033[0m" , end='')
        j = 13
        st = ""
        if len(self.state.board[j]) > 1:
            print("\033[32m| " , end='')
            for k in range(len(self.state.board[j])):
                if k%2 == 0 and self.state.board[j][k] != 's':
                    st += f"{colores[ord(self.state.board[j][k]) - ord('0')]}{self.state.board[j][k+1:k+2]}\033[0m"
                elif self.state.board[j][k] == 's':
                    st += "\033[32ms\033[0m"
            num = (9 - (len(st) - (int(len(self.state.board[j])/2) + 1*(len(self.state.board[j])%2!=0))*9))
            for _ in range(num):
                st = st + " "
            print(st, end='')
        else:
            print(f"\033[32m| {self.state.board[j]:^9} \033[0m" , end='')
        j = 26
        st = ""
        if len(self.state.board[j]) > 1:
            print("\033[33m| " , end='')
            for k in range(len(self.state.board[j])):
                if k%2 == 0 and self.state.board[j][k] != 's':
                    st += f"{colores[ord(self.state.board[j][k]) - ord('0')]}{self.state.board[j][k+1:k+2]}\033[0m"
                elif self.state.board[j][k] == 's':
                    st += "\033[33ms\033[0m"
            num = (9 - (len(st) - (int(len(self.state.board[j])/2) + 1*(len(self.state.board[j])%2!=0))*9))
            for _ in range(num):
                st = st + " "
            print(st, end='')
        else:
            print(f"\033[33m| {self.state.board[j]:^9} \033[0m" , end='')
        j = 39
        st = ""
        if len(self.state.board[j]) > 1:
            print("\033[34m| " , end='')
            for k in range(len(self.state.board[j])):
                if k%2 == 0 and self.state.board[j][k] != 's':
                    st += f"{colores[ord(self.state.board[j][k]) - ord('0')]}{self.state.board[j][k+1:k+2]}\033[0m"
                elif self.state.board[j][k] == 's':
                    st += "\033[34ms\033[0m"
            num = (9 - (len(st) - (int(len(self.state.board[j])/2) + 1*(len(self.state.board[j])%2!=0))*9))
            for _ in range(num):
                st = st + " "
            print(st, end='')
            print("|")
        else:
            print(f"\033[34m| {self.state.board[j]:^9} |\033[0m")
        print("-" * 49) 

       # iterate to print the board
        for i in range (1 , 13):
             j = i
             st = ""
             if len(self.state.board[j]) > 1: 
                print("| " , end='')
                for k in range(len(self.state.board[j])):
                    if k%2 == 0 and self.state.board[j][k] != 's':
                        st += f"{colores[ord(self.state.board[j][k]) - ord('0')]}{self.state.board[j][k+1:k+2]}\033[0m"
                    elif self.state.board[j][k] == 's':
                        st+= "s"
                num = (9 - (len(st) - (int(len(self.state.board[j])/2))*9))
                for _ in range(num):
                    st = st + " "
                print(st, end='')
             else:
                print(f"| {self.state.board[j]:^9} " , end='')
                
             j += 13
             st = ""
             if len(self.state.board[j]) > 1: 
                print("| " , end='')
                for k in range(len(self.state.board[j])):
                    if k%2 == 0 and self.state.board[j][k] != 's':
                        st += f"{colores[ord(self.state.board[j][k]) - ord('0')]}{self.state.board[j][k+1:k+2]}\033[0m"
                    elif self.state.board[j][k] == 's':
                        st+= "s"
                num = (9 - (len(st) - (int(len(self.state.board[j])/2))*9))
                for _ in range(num):
                    st = st + " "
                print(st, end='')
             else:
                print(f"| {self.state.board[j]:^9} " , end='')
             j += 13
             st = ""
             if len(self.state.board[j]) > 1: 
                print("| " , end='')
                for k in range(len(self.state.board[j])):
                    if k%2 == 0 and self.state.board[j][k] != 's':
                        st += f"{colores[ord(self.state.board[j][k]) - ord('0')]}{self.state.board[j][k+1:k+2]}\033[0m"
                    elif self.state.board[j][k] == 's':
                        st+= "s"
                num = (9 - (len(st) - (int(len(self.state.board[j])/2))*9))
                for _ in range(num):
                    st = st + " "
                print(st, end='')
             else:
                print(f"| {self.state.board[j]:^9} " , end='')
             j += 13
             st = ""
             if len(self.state.board[j]) > 1: 
                print("| " , end='')
                for k in range(len(self.state.board[j])):
                    if k%2 == 0 and self.state.board[j][k] != 's':
                        st += f"{colores[ord(self.state.board[j][k]) - ord('0')]}{self.state.board[j][k+1:k+2]:^9}\033[0m"
                    elif self.state.board[j][k] == 's':
                        st+= "s"
                num = (9 - (len(st) - (int(len(self.state.board[j])/2))*9))
                for _ in range(num):
                    st = st + " "
                print(st , end='')
                print("|")
             else:
                print(f"| {self.state.board[j]:^9} |")
             print("-" * 49)
# Logic Class
class Logic:
    def __init__(self):
        self.visited = {}
        


    def Pieces_To_Move(self ,dice , P_Moves):
        pieces = {}
        for moves in P_Moves:
            if moves[1] == dice:
                pieces[moves[0]] = 1
        for piece in pieces:
            print(piece)
        return pieces
        
    
    def play4Humans(self):
        node =  Node(4)
        while(node.Is_Win() != True):
            node.Print_State()
            cntWin=0
            for i in range(4):
                if node.state.piece[node.WhoIsNextPlayer()][i]==-2: cntWin+=1
            temp = self.PlayHuman(node)
            if(temp == None):continue
            else: node = temp
            
        print(f"\033[32mPlayer {node.player} Won\033[0m")

    def Play(self):
        node =  Node()
        while(node.Is_Win() != True):
            node.Print_State()
            cntWin=0
            for i in range(4):
                if node.state.piece[node.WhoIsNextPlayer()][i]==-2: cntWin+=1
            if node.WhoIsNextPlayer() == 0:
                temp = self.PlayHuman(node)
                if(temp == None):continue
                else: node = temp
            else: 
                node = self.PlayComputer(node)
            cntWin2=0
            for i in range(4):
                if node.state.piece[node.player][i]==-2: cntWin2+=1
            if cntWin!=cntWin2: print(f"\033[32mpiece is in win path\033[0m")
            
        print(f"\033[32mPlayer {node.player} Won\033[0m")


    def PlayHuman(self , node : Node):
        P_actions = node.Generate_Next_States()
        Roll = input("Roll The Dice : (Type F)")
        if(Roll == 'F' or Roll == 'f'):
            dice = random.randint(1 , 6)
        else:
            print("\033[31mTry Again Please\033[0m")
            return None
        print(f'Turn : {node.WhoIsNextPlayer()}')
        print(f'Dice : {dice}')
        print("Available Moves : ")
        pieces = self.Pieces_To_Move( dice, P_actions)
        print(P_actions)
        Piece = 0
        if(len(pieces) > 0):
            Piece = input("Choose from the available Pieces : ")
        else:
            print("\033[31m No Availabe Move\033[0m")
        node=node.Apply_Move(int(Piece) , dice)
        return node

    def PlayComputer(self , node : Node):
        dice = random.randint(1 , 6)
        temp = self.expectminmax(2 , node , False , 5 , 1 , dice)
        print(f"best Piece is {temp[0]}")
        print(f'Turn : {2}')
        print(f'Dice : {dice}')
        return node.Apply_Move(temp[0] , dice)

            
    
    def expectminmax(self , turn  , node : Node , chance , depth , piece , dice):
        P_Actions = node.Generate_Next_States()
        if depth == 0 or node.Is_Win == True:           
            ev = 0
            cnt = 0
            for i in range(1 , 7):
                if node.nextnodes[piece][i]!= None: 
                    cnt += 1
                    ev += node.nextnodes[piece][i].chance[node.player] # think again
            temp = -100000
            if cnt > 0: temp = ev / cnt
            if node.player == 0: temp *= -1 
            return (piece ,  temp)
        expected = 0
        value = -1000000000
        BestPiece = -1
        if turn == 0: value *= -1                
        if chance == False:
            for i in range(4):
                can = False
                for j in P_Actions:
                    if j[1] == dice and j[0] == i:
                        can = True  
                if can == True:
                    temp = self.expectminmax(turn , node , True , depth-1 , i , dice)
                    if (turn == 2 and temp[1] > value) or (turn == 0 and temp[1] < value):
                        value = temp[1]
                        BestPiece = i                   
            return (BestPiece , value)
        cnt = 0
        for i in range(1,7):
            if node.nextnodes[piece][i]!= None: 
                temp = self.expectminmax(node.WhoIsNextPlayer() , node.nextnodes[piece][i] , False , depth-1 , piece , i)
                expected += temp[1]
                cnt += 1
        temp = -100000
        if cnt > 0: temp = expected / cnt
        if node.player == 0: temp *= -1  
        return (piece , temp)

