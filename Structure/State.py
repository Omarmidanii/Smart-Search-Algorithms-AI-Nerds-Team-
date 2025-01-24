import numpy as np
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
    
