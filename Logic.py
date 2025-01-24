from Structure.Node import Node
import random
import numpy as np
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


        



