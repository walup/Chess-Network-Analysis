from enum import Enum
import numpy as np
import matplotlib.pyplot as plt
import copy
from PIL import Image
from matplotlib.offsetbox import (OffsetImage, AnnotationBbox)
from matplotlib.patches import Rectangle

class PieceImageRenderer:
    
    def __init__(self, imageFolder):
        self.imageFolder = imageFolder
        self.imageDict = {}
        self.imageDict[PieceType.PAWN, PieceColor.BLACK] = imageFolder + "/black_pawn.png"
        self.imageDict[PieceType.PAWN, PieceColor.WHITE] = imageFolder + "/white_pawn.png"
        self.imageDict[PieceType.BISHOP, PieceColor.BLACK] = imageFolder + "/black_bishop.png"
        self.imageDict[PieceType.BISHOP, PieceColor.WHITE] = imageFolder + "/white_bishop.png"
        self.imageDict[PieceType.KNIGHT, PieceColor.BLACK] = imageFolder + "/black_knight.png"
        self.imageDict[PieceType.KNIGHT, PieceColor.WHITE] = imageFolder + "/white_knight.png"
        self.imageDict[PieceType.ROOK, PieceColor.WHITE] = imageFolder + "/white_rook.png"
        self.imageDict[PieceType.ROOK, PieceColor.BLACK] = imageFolder + "/black_rook.png"
        self.imageDict[PieceType.QUEEN, PieceColor.WHITE] = imageFolder + "/white_queen.png"
        self.imageDict[PieceType.QUEEN, PieceColor.BLACK] = imageFolder + "/black_queen.png"
        self.imageDict[PieceType.KING, PieceColor.WHITE] = imageFolder + "/white_king.png"
        self.imageDict[PieceType.KING, PieceColor.BLACK] = imageFolder + "/black_king.png"
        
    def getPieceImage(self, width, height, pieceType, pieceColor):
        urlImage = self.imageDict[pieceType, pieceColor]
        image = Image.open(urlImage)
        return image.resize((width, height))
    

class PieceType(Enum):
    PAWN = ""
    ROOK = "R"
    KNIGHT = "N"
    QUEEN = "Q"
    BISHOP = "B"
    KING = "K"
    
class PieceColor(Enum):
    WHITE = 0
    BLACK = 1

class ChessCoordinateTranslator:
    
    def __init__(self):
        self.fileNames = ["a", "b", "c", "d", "e", "f", "g", "h"]
        self.rankNames = ["1","2","3","4","5","6","7","8"]
    
    def getMatrixCoordinates(self, file, rank):
        '''
        Computes matrix coordinates:
        
        a-h go to 0-7
        1-8 go to 7-0 (y-axis is inverted)
        '''
        row = -1
        col = -1
        for i in range(0,len(self.fileNames)):
            if(self.fileNames[i] == file):
                col = i
                break
        
        row = 8-int(rank)
        
        return [row, col]
    
    def getChessNotationCoordinates(self, row, col):
        '''
        Gets chess notation coordinates from matrix coordinates
        '''
        file = self.fileNames[col]
        rank = self.rankNames[7-row]
        return [file, rank]
    
    def getImageCoordinates(self, file, rank):
        row = -1
        col = -1
        for i in range(0,len(self.fileNames)):
            if(self.fileNames[i] == file):
                col = i
                break
        
        row = int(rank)-1
        
        return [row, col]
        

    
class ChessMove:
    
    def __init__(self, moveString):
        self.moveString = moveString
        self.specialSymbols =["x", "+", "#", "=", "N", "Q", "K", "R", "B"]
        self.takes = "x" in self.moveString
        self.check = "+" in self.moveString
        self.checkMate = "#" in self.moveString
    
    @classmethod
    def fromChessCoordinates(cls, pieceType, fromFile, fromRank, toFile, toRank, takes, castleMove, promotionPiece, check, checkmate):
        if(castleMove == "O-O-O" or castleMove == "O-O"):
            moveString = castleMove + checkmate + check
            return cls(moveString)
        
        else:
            moveString = pieceType + fromFile + fromRank + takes + toFile + toRank
            
            if(promotionPiece != ""):
                moveString = moveString + "=" +promotionPiece
            
            moveString = moveString + checkmate + check
            
            return cls(moveString)
        
    
    def specifyFromPosition(self, file, rank):
        if(self.moveString[0] in ["N", "Q", "K", "R", "B"]):
            self.moveString = self.moveString[0] + file + rank +self.moveString[1:]
        
    def __eq__(self, other):
        return self.moveString == other.moveString
    
    def reduceMoveString(self,moveString):
        reducedString = moveString
        for i in range(0,len(self.specialSymbols)):
            reducedString = reducedString.replace(self.specialSymbols[i], "")
        
        return reducedString
        
    def executeMove(self, piece):
        '''
        Moves a piece into the position indicated by the move. The method also throws 
        indicators tha tells if a piece has been taken, and if there's a check or a
        checkmate. 
        '''
        
        takes = False
        check = False
        
        takes = "x" in self.moveString
        check = "+" in self.moveString
        checkMate = "#" in self.moveString
        
        #Castling short
        reducedString = self.reduceMoveString(self.moveString)
        if(reducedString =="O-O"):
            if(piece.pieceType == PieceType.KING):
                piece.setPosition("g",piece.rank)
            
            elif(piece.pieceType == PieceType.ROOK):
                piece.setPosition("f",piece.rank)
        
        #Castling long
        elif(reducedString == "O-O-O"):
            if(piece.pieceType == PieceType.KING):
                piece.setPosition("c", piece.rank)
            
            elif(piece.pieceType == PieceType.ROOK):
                piece.setPosition("d", piece.rank)
        
        #Others
        elif("=" in self.moveString):
            reducedString = self.moveString.split("=")[1].replace("+","").replace("#","")
            #Promotions change the piece type
            pieceType = PieceType(reducedString)
            piece.setPieceType(pieceType)
            
            #Set the new position for the piece
            newPosition = self.getPieceFinalPosition()
            piece.setPosition(newPosition[0],newPosition[1])
        
        #Normal move
        else:
            newPosition = self.getPieceFinalPosition()
            piece.setPosition(newPosition[0],newPosition[1])
        
        #Increment the number of moves of the piece
        piece.increaseMoveCounter()
            
        return takes, check, checkMate
    
    def getPieceFinalPosition(self):
        reducedString = self.reduceMoveString(self.moveString)
        file = reducedString[-2]
        rank = reducedString[-1]
            
        
        return [file, rank]
        
        
            
    
    
class ChessPiece:
    
    def __init__(self, pieceType, pieceColor, file, rank):
        
        self.pieceType = pieceType
        self.file = file
        self.rank = rank
        self.pieceColor = pieceColor
        self.pieceMoves = []
        self.moveCounter = 0
        self.winner = -1
    
    def getPieceDescription(self):
        description = ""
        description = description + "File: "+self.file + "\n"
        description = description + "Rank: "+self.rank + "\n"
        description = description + "Type: " + str(self.pieceType)+"\n"
        description = description + "Color: " + str(self.pieceColor)+"\n"
        description = description + "Moves: "+ "\n\n"
        movesPerRow = 5
        for i in range(0,len(self.pieceMoves)):
            description = description + self.pieceMoves[i].moveString + "  "
            if(i !=0 and (i%movesPerRow) == 0):
                description = description + "\n"
        
        return description
    
    def __eq__(self, other):
        return self.pieceType == other.pieceType and self.pieceColor == other.pieceColor and self.file == other.file and self.rank == other.rank
    
    def setPosition(self, file, rank):
        self.file = file
        self.rank = rank
        
    def setPieceType(self, pieceType):
        self.pieceType = pieceType
    
    def getPieceMoves(self):
        return self.pieceMoves
        
    def increaseMoveCounter(self):
        self.moveCounter = self.moveCounter + 1
        
    def addMove(self, move):
        if(not move in self.pieceMoves):
            self.pieceMoves.append(move)
    
    def resetPieceMoves(self):
        self.pieceMoves = []
    
    def computePieceMoves(self, board, checkGlobal, checkmateGlobal):
        #If checkmate has been played there are no moves left!, Game Over
        
        if(checkmateGlobal):
            self.pieceMoves = []
        
        #We want to do moves that get the king out of check. 
        elif(checkGlobal):
            fileVision, rankVision, takesArray = board.getPieceBoardVision(self.pieceType, self.file, self.rank, self.moveCounter, self.pieceColor)
            for i in range(0,len(fileVision)):
                #Which of these moves get us out of check
                if(not board.isKingInCheckAfterMoving(self, self.pieceType, fileVision[i], rankVision[i], self.pieceColor)):
                    
                    pieceType = self.pieceType.value
                    
                    file = fileVision[i]
                    rank = rankVision[i]
                    
                    isDestinationShared, otherPieceFile, otherPieceRank, conflictMove = board.isDestinationSquareShared(self, self.pieceType, self.pieceColor, file, rank)
                    
                    if(isDestinationShared):
                        if(otherPieceFile != file and otherPieceRank != rank):
                            otherPieceRank = ""
                        
                        
                        elif(otherPieceFile == file):
                            otherPieceFile = ""
                        
                        elif(otherPieceRank == rank):
                            otherPieceRank = ""
                        
                        conflictMove.specifyFromPosition(otherPieceFile, otherPieceRank)
                    
                    fromFile = ""
                    fromRank = ""
                    if(isDestinationShared and otherPieceFile != ""):
                        fromFile = self.file
                    if(isDestinationShared and otherPieceRank != ""):
                        fromRank = self.rank
                    
                    
                        
                    takes = ""
                    if(takesArray[i] == True):
                        takes = "x"
                        if(self.pieceType == PieceType.PAWN):
                            pieceType = self.file
                    
                    
                    castleMove = ""
                    #Pawn promotion
                    if(self.pieceType == PieceType.PAWN and (rank == "8" or rank == "1")):
                        pieceLetters = ["Q", "R", "B", "N"]
                        for j in range(0,len(pieceLetters)):
                            checkCondition, checkmateCondition = board.isEnemyKingCheckmatedAfterMove(self,PieceType(pieceLetters[j]), file, rank, self.pieceColor, checkGlobal)
                            check = ""
                            checkmate = ""
                            if(checkmateCondition):
                                checkmate = "#"
                            elif(checkCondition):
                                check = "+"
                            
                            move = ChessMove.fromChessCoordinates(pieceType, fromFile, fromRank, file, rank, takes, castleMove, pieceLetters[j], check, checkmate)
                            self.addMove(move)
                    else:
                        promotion = ""
                        check = ""
                        checkmate = ""
                        checkCondition, checkmateCondition = board.isEnemyKingCheckmatedAfterMove(self, self.pieceType, file, rank, self.pieceColor, checkGlobal)
                        if(checkmateCondition):
                            checkmate = "#"
                        elif(check):
                            check = "+"
                            
                        move = ChessMove.fromChessCoordinates(pieceType, fromFile, fromRank, file, rank, takes, castleMove, promotion, check, checkmate)
                        #print(move.moveString)
                        self.addMove(move)
                        
                         
        else:
            fileVision, rankVision, takesArray = board.getPieceBoardVision(self.pieceType, self.file, self.rank, self.moveCounter, self.pieceColor)
                
            for i in range(0,len(fileVision)):
                pieceType = self.pieceType.value
                file = fileVision[i]
                rank = rankVision[i]
                #Castle king case 
                
                if(self.pieceType == PieceType.KING and not board.isKingInCheckAfterMoving(self, self.pieceType, fileVision[i], rankVision[i], self.pieceColor) and ((self.file == "e" and file == "g") or (self.file == "e" and file == "c"))):
                    castleMove = ""
                    #Castling short case
                    if(self.file == "e" and file == "g"):
                        castleMove = "O-O"
                        check = ""
                        checkmate = ""
                        rook = board.getPieceAtPosition("h",self.rank)
                        checkCondition, checkmateCondition = board.isEnemyKingCheckmatedAfterMove(rook, rook.pieceType,"f", rook.rank, self.pieceColor,checkGlobal)
                        if(checkmateCondition):
                            checkmate = "#"
                        elif(check):
                            check = "+"
                        
                        move = ChessMove.fromChessCoordinates("", "", "", "", "", "", castleMove, "", check, checkmate)
                        rook.addMove(move)
                        self.addMove(move)
                    elif(self.file == "e" and file == "c"):
                        castleMove = "O-O-O"
                        check = ""
                        checkmate = ""
                        rook = board.getPieceAtPosition("a",self.rank)
                        checkCondition, checkmateCondition = board.isEnemyKingCheckmatedAfterMove(rook, rook.pieceType,"d", rook.rank, self.pieceColor, checkGlobal)
                        if(checkmateCondition):
                            checkmate = "#"
                        elif(check):
                            check = "+"
                        move = ChessMove.fromChessCoordinates("", "", "", "", "", "", castleMove, "", check, checkmate)
                        rook.addMove(move)
                        self.addMove(move)
      
                #Pawn promotion
                elif(self.pieceType == PieceType.PAWN and (rank == "1" or rank == "8") and not board.isKingInCheckAfterMoving(self, self.pieceType, fileVision[i], rankVision[i], self.pieceColor)):
                    
                    castleMove = ""
                    otherPieceFile = ""
                    otherPieceRank = ""
                    
                    takes = ""
                    if(takesArray[i] == True):
                        takes = "x"
                        pieceType = self.file
                    
                    pieceLetters = ["Q", "R", "B", "N"]
                    for j in range(0,len(pieceLetters)):
                        checkCondition, checkmateCondition = board.isEnemyKingCheckmatedAfterMove(self, PieceType(pieceLetters[j]), file, rank, self.pieceColor, checkGlobal)
                        check = ""
                        checkmate = ""
                        if(checkmateCondition):
                            checkmate = "#"
                        elif(checkCondition):
                            check = "+"
                            
                        move = ChessMove.fromChessCoordinates(pieceType, otherPieceFile, otherPieceRank, file, rank, takes, castleMove, pieceLetters[j], check, checkmate)
                        self.addMove(move)
                
                
                
                elif(not board.isKingInCheckAfterMoving(self, self.pieceType, fileVision[i], rankVision[i], self.pieceColor)):

                    isDestinationShared, otherPieceFile, otherPieceRank, conflictingMove = board.isDestinationSquareShared(self, self.pieceType, self.pieceColor, file, rank)
                    
                    if(isDestinationShared):
                        if(otherPieceFile != file and otherPieceRank != rank):
                            otherPieceRank = ""
                        
                        
                        elif(otherPieceFile == file):
                            otherPieceFile = ""
                        
                        elif(otherPieceRank == rank):
                            otherPieceRank = ""
                        
                        conflictingMove.specifyFromPosition(otherPieceFile, otherPieceRank)
                        
                    
                    fromFile = ""
                    fromRank = ""
                    if(isDestinationShared and otherPieceFile != ""):
                        fromFile = self.file
                    if(isDestinationShared and otherPieceRank != ""):
                        fromRank = self.rank
                        
                    
                    takes = ""
                    if(takesArray[i] == True):
                        takes = "x"
                        if(self.pieceType == PieceType.PAWN):
                            pieceType = self.file
                    
                    castleMove = ""
                    
                    checkCondition, checkmateCondition = board.isEnemyKingCheckmatedAfterMove(self,self.pieceType, file, rank, self.pieceColor, checkGlobal)
                    check = ""
                    checkmate = ""
                    promotion = ""
                    if(checkmateCondition):
                        checkmate = "#"
                    elif(checkCondition):
                        check = "+"
                            
                    move = ChessMove.fromChessCoordinates(pieceType, fromFile, fromRank, file, rank, takes, castleMove,promotion , check, checkmate)
                    self.addMove(move)

class ChessBoard:
    
    def __init__(self):
        self.pieces = []
        self.moveNumber = 0
        self.blackColor = "#c9782c"
        self.whiteColor = "#f2dbc4"
        self.gameEnded = False
        self.executedMoves = []
    
    def getMaterial(self):
        
        nPieces = len(self.pieces)
        material = 0
        for i in range(0,nPieces):
            sign = 1
            piece = self.pieces[i]
            if(piece.pieceColor == PieceColor.BLACK):
                sign = -1
            
            if(piece.pieceType == PieceType.PAWN):
                material = material + sign*1
            
            elif(piece.pieceType == PieceType.BISHOP or piece.pieceType == PieceType.KNIGHT):
                material = material + sign*3
            
            elif(piece.pieceType == PieceType.ROOK):
                material = material + sign*5
            
            elif(piece.pieceType == PieceType.QUEEN):
                material = material + sign*9
        
        return material
    
    def getSpace(self, color):
        enemyRanks = ["5","6","7","8"]
        if(color == PieceColor.BLACK):
            enemyRanks = ["1","2","3","4"]
        
        nPieces = len(self.pieces)
        space = 0
        registered = []
        for i in range(0,nPieces):
            piece = self.pieces[i]
            if(piece.pieceColor == color):
                #Get the vision
                visionFiles, visionRanks, takes = self.getPieceBoardVision(piece.pieceType,piece.file, piece.rank, piece.moveCounter, color)
                for j in range(0,len(visionRanks)):
                    position = [visionFiles[j], visionRanks[j]]
                    if(visionRanks[j] in enemyRanks and (not position in registered)):
                        space = space + 1
                        registered.append(position)
        
        return space
                        
            
    
    def isOccupied(self, file, rank):
        for i in range(0,len(self.pieces)):
            if(self.pieces[i].file == file and self.pieces[i].rank == rank):
                return True
            
        return False
    
    def isOccupiedByEnemyPiece(self, file, rank, enemyColor):
        for i in range(0,len(self.pieces)):
            if(self.pieces[i].file == file and self.pieces[i].rank == rank and self.pieces[i].pieceColor == enemyColor):
                return True
        
        return False
    
    def getPieceAtPosition(self, file, rank):
        for i in range(0,len(self.pieces)):
            if(self.pieces[i].file == file and self.pieces[i].rank == rank):
                return self.pieces[i]
        
        return None
            
    def isKingInCheckAfterMoving(self, piece, newPieceType, file, rank, pieceColor):
        originalFile = piece.file
        originalRank = piece.rank
        originalType = piece.pieceType
        
        indexRemoved = -1
        removedPiece = self.getPieceAtPosition(file, rank)
        if((not removedPiece is None) and removedPiece.pieceType != PieceType.KING and pieceColor != removedPiece.pieceColor):
            indexRemoved = self.pieces.index(removedPiece)
            self.pieces.remove(removedPiece)
        
        piece.file = file
        piece.rank = rank 
        piece.pieceType = newPieceType
        
        king = -1
        for i in range(0,len(self.pieces)):
            if(self.pieces[i].pieceType == PieceType.KING and self.pieces[i].pieceColor == pieceColor):
                king = self.pieces[i]
        
        kingFile = king.file
        kingRank = king.rank
        check = False
        for i in range(0,len(self.pieces)):
            if(self.pieces[i].pieceColor != pieceColor):
                visionFiles, visionRanks, takes = self.getPieceBoardVision(self.pieces[i].pieceType, self.pieces[i].file, self.pieces[i].rank, self.pieces[i].moveCounter, self.pieces[i].pieceColor)
                checkFound = False
                for j in range(0,len(visionFiles)):
                    if(kingFile == visionFiles[j] and kingRank == visionRanks[j]):
                        check = True
                        checkFound = True
                        break
                    
                if(checkFound):
                    break
                    
        
        piece.file = originalFile
        piece.rank = originalRank
        piece.pieceType = originalType
        
        if((not removedPiece is None) and removedPiece.pieceType != PieceType.KING and pieceColor != removedPiece.pieceColor):
            self.pieces.insert(indexRemoved, removedPiece)
        
        return check
                
    
    def isEnemyKingInCheckAfterMoving(self, piece, newPieceType, file, rank, pieceColor):
        #First let's get the enemy king 
        enemyColor = PieceColor.BLACK
        if(pieceColor == PieceColor.BLACK):
            enemyColor = PieceColor.WHITE
        king = -1
        
        for i in range(0,len(self.pieces)):
            if(self.pieces[i].pieceType == PieceType.KING and self.pieces[i].pieceColor == enemyColor):
                king = self.pieces[i]
                break
        
        kingFile = king.file
        kingRank = king.rank
        
        #Move the piece provisionally
        originalFile = piece.file
        originalRank = piece.rank
        originalType = piece.pieceType
        
        removedPiece = self.getPieceAtPosition(file, rank)
        indexRemoved = -1
        if((not removedPiece is None) and removedPiece.pieceType != PieceType.KING and pieceColor != removedPiece.pieceColor):
            indexRemoved = self.pieces.index(removedPiece)
            self.pieces.remove(removedPiece)
        
        
        piece.file = file
        piece.rank = rank
        piece.pieceType = newPieceType
        
        #Get the board vision of files under this 
        #and see if the king is seen by any pieces
        
        check = False
        for i in range(0,len(self.pieces)):
            if(self.pieces[i].pieceColor == pieceColor):
                visionFiles, visionRanks, takes = self.getPieceBoardVision(self.pieces[i].pieceType, self.pieces[i].file, self.pieces[i].rank, self.pieces[i].moveCounter, self.pieces[i].pieceColor)
                checkFound = False
                for j in range(0,len(visionFiles)):
                    if(kingFile == visionFiles[j] and kingRank == visionRanks[j]):
                        check = True
                        checkFound = True
                        break
                if(checkFound):
                    break
                    
        
        if((not removedPiece is None) and removedPiece.pieceType != PieceType.KING and pieceColor != removedPiece.pieceColor):
            self.pieces.insert(indexRemoved, removedPiece)
        
        piece.file = originalFile
        piece.rank = originalRank
        piece.pieceType = originalType
        
        
        
        return check
        
        
    
    
    def isEnemyKingCheckmatedAfterMove(self, piece, newPieceType, file, rank, pieceColor, checkGlobal):
        check = self.isEnemyKingInCheckAfterMoving(piece, newPieceType, file, rank, pieceColor)
        checkmated = False
        if(check):
            checkmated = True
            removedIndex = -1
            removedPiece = self.getPieceAtPosition(file, rank)
            if((not removedPiece is None) and removedPiece.pieceType != PieceType.KING and pieceColor != removedPiece.pieceColor):
                removedIndex = self.pieces.index(removedPiece)
                self.pieces.remove(removedPiece)
            
            originalFile = piece.file
            originalRank = piece.rank
            originalType = piece.pieceType
            
            piece.file = file
            piece.rank = rank
            piece.pieceType = newPieceType
            
            notCheckmated = False
            for i in range(0,len(self.pieces)):
                if(self.pieces[i].pieceColor != pieceColor):
                    fileVision, rankVision, takesArray = self.getPieceBoardVision(self.pieces[i].pieceType, self.pieces[i].file, self.pieces[i].rank, self.pieces[i].moveCounter, self.pieces[i].pieceColor)
                    for j in range(0,len(fileVision)):
                        if(not self.isKingInCheckAfterMoving(self.pieces[i], self.pieces[i].pieceType, fileVision[j], rankVision[j], self.pieces[i].pieceColor)):
                            checkmated = False
                            notCheckmated = True
                            break
                    if(notCheckmated):
                        break
            
            piece.file = originalFile
            piece.rank = originalRank
            piece.pieceType = originalType
            
            
            if((not removedPiece is None) and removedPiece.pieceType != PieceType.KING and pieceColor != removedPiece.pieceColor):
                self.pieces.insert(removedIndex, removedPiece)
        
        return check, checkmated

                    
    def addPiece(self, pieceType, pieceColor, file, rank):
        piece = ChessPiece(pieceType, pieceColor, file, rank)
        if(not piece in self.pieces):
            self.pieces.append(piece)
    
    def getPieceBoardVision(self, pieceType, file, rank, pieceMoveCounter, pieceColor):
        visionFiles = []
        visionRanks = []
        takes = []
        
        translator = ChessCoordinateTranslator()
        
        matrixCoords = translator.getMatrixCoordinates(file, rank)
        enemyColor = PieceColor.BLACK
        if(pieceColor == PieceColor.BLACK):
            enemyColor = PieceColor.WHITE
        
        if(pieceType == PieceType.PAWN):
            if(pieceColor == PieceColor.WHITE):
                #Move forward
                index1 = matrixCoords[0]-1
                index2 = matrixCoords[1]
            
                if(index1 >= 0):
                    translated = translator.getChessNotationCoordinates(index1, index2)
                    if(not self.isOccupied(translated[0], translated[1])):
                        visionFiles.append(translated[0])
                        visionRanks.append(translated[1])
                        takes.append(False)
            
                #Two moves forward 
                index1 = matrixCoords[0]-2
                index2 = matrixCoords[1]
  
                if(index1 >= 0 and pieceMoveCounter == 0):
                    translated = translator.getChessNotationCoordinates(index1, index2)
                    if(not self.isOccupied(translated[0], translated[1])):
                        visionFiles.append(translated[0])
                        visionRanks.append(translated[1])
                        takes.append(False)
            
                #Diagonal takes
                index1 = matrixCoords[0]-1
                index2 = matrixCoords[1]-1
                if(index1 >= 0 and index2 >= 0):
                    translated = translator.getChessNotationCoordinates(index1, index2)
                    if(self.isOccupiedByEnemyPiece(translated[0], translated[1], enemyColor)):
                        visionFiles.append(translated[0])
                        visionRanks.append(translated[1])
                        takes.append(True)
            
                index1 = matrixCoords[0] - 1
                index2 = matrixCoords[1] + 1
        
                if(index1 >= 0 and index2 <= 7):
                    translated = translator.getChessNotationCoordinates(index1, index2)
                    if(self.isOccupiedByEnemyPiece(translated[0], translated[1], enemyColor)):
                        visionFiles.append(translated[0])
                        visionRanks.append(translated[1])
                        takes.append(True)
            
                #En passant
                if(matrixCoords[0] == 4):
                    index1 = matrixCoords[0]
                    index2 = matrixCoords[1]+1
                    candidate1 = self.getPieceAtPosition(index1, index2)
                    if(candidate1 != None and candidate1.pieceColor == enemyColor and candidate1.moveCounter == 1):
                        translated = translator.getChessNotationCoordinates(index1-1, index2)
                        visionFiles.append(translated[0])
                        visionRanks.append(translated[1])
                        takes.append(True)
                
                    index1 = matrixCoords[0]
                    index2 = matrixCoords[1]-1
                    candidate2 = self.getPieceAtPosition(index1, index2)
                    if(candidate2 != None and candidate2.pieceColor == enemyColor and candidate2.moveCounter == 1):
                        translated = translator.getChessNotationCoordinates(index1-1, index2)
                        visionFiles.append(translated[0])
                        visionRanks.append(translated[1])
                        takes.append(True)
            
            elif(pieceColor == PieceColor.BLACK):
                #Move forward
                index1 = matrixCoords[0]+1
                index2 = matrixCoords[1]
            
                if(index1 <= 7):
                    translated = translator.getChessNotationCoordinates(index1, index2)
                    if(not self.isOccupied(translated[0], translated[1])):
                        visionFiles.append(translated[0])
                        visionRanks.append(translated[1])
                        takes.append(False)
            
                #Two moves forward 
                index1 = matrixCoords[0]+2
                index2 = matrixCoords[1]
  
                if(index1 <=7 and pieceMoveCounter == 0):
                    translated = translator.getChessNotationCoordinates(index1, index2)
                    if(not self.isOccupied(translated[0], translated[1])):
                        visionFiles.append(translated[0])
                        visionRanks.append(translated[1])
                        takes.append(False)
            
                #Diagonal takes
                index1 = matrixCoords[0]+1
                index2 = matrixCoords[1]-1
                if(index1 <= 7 and index2 >= 0):
                    translated = translator.getChessNotationCoordinates(index1, index2)
                    if(self.isOccupiedByEnemyPiece(translated[0], translated[1], enemyColor)):
                        visionFiles.append(translated[0])
                        visionRanks.append(translated[1])
                        takes.append(True)
            
                index1 = matrixCoords[0] + 1
                index2 = matrixCoords[1] + 1
        
                if(index1 <= 7 and index2 <= 7):
                    translated = translator.getChessNotationCoordinates(index1, index2)
                    if(self.isOccupiedByEnemyPiece(translated[0], translated[1], enemyColor)):
                        visionFiles.append(translated[0])
                        visionRanks.append(translated[1])
                        takes.append(True)
            
                #En passant
                if(matrixCoords[0] == 3):
                    index1 = matrixCoords[0]
                    index2 = matrixCoords[1]+1
                    candidate1 = self.getPieceAtPosition(index1, index2)
                    if(candidate1 != None and candidate1.pieceColor == enemyColor and candidate1.moveCounter == 1):
                        translated = translator.getChessNotationCoordinates(index1-1, index2)
                        visionFiles.append(translated[0])
                        visionRanks.append(translated[1])
                        takes.append(True)
                
                    index1 = matrixCoords[0]
                    index2 = matrixCoords[1]-1
                    candidate2 = self.getPieceAtPosition(index1, index2)
                    if(candidate2 != None and candidate2.pieceColor == enemyColor and candidate2.moveCounter == 1):
                        translated = translator.getChessNotationCoordinates(index1-1, index2)
                        visionFiles.append(translated[0])
                        visionRanks.append(translated[1])
                        takes.append(True)
            
                    
        elif(pieceType == PieceType.BISHOP):
            #Examine the 4 semi diagonals 
            for i in range(1,8):
                index1 = matrixCoords[0] - i
                index2 = matrixCoords[1] + i
                if(index1 >= 0 and index2 <= 7):
                    translated = translator.getChessNotationCoordinates(index1, index2)
                    obstructingPiece = self.getPieceAtPosition(translated[0], translated[1])
                    if(not obstructingPiece is None):
                        if(obstructingPiece.pieceColor == enemyColor):
                            visionFiles.append(translated[0])
                            visionRanks.append(translated[1])
                            takes.append(True)
                    
                        break
                        
                    else:
                        visionFiles.append(translated[0])
                        visionRanks.append(translated[1])
                        takes.append(False)

            for i in range(1,8):
                index1 = matrixCoords[0] + i
                index2 =  matrixCoords[1] - i
                if(index1 <= 7 and index2 >= 0):
                    translated = translator.getChessNotationCoordinates(index1, index2)
                    obstructingPiece = self.getPieceAtPosition(translated[0], translated[1])
                    if(not obstructingPiece is None):
                        if(obstructingPiece.pieceColor == enemyColor):
                            visionFiles.append(translated[0])
                            visionRanks.append(translated[1])
                            takes.append(True)
                    
                        break
                        
                    else:
                        visionFiles.append(translated[0])
                        visionRanks.append(translated[1])
                        takes.append(False)
                        
            for i in range(1,8):
                index1 = matrixCoords[0] + i
                index2 =  matrixCoords[1] + i
                if(index1 <= 7 and index2 <= 7):
                    translated = translator.getChessNotationCoordinates(index1, index2)
                    obstructingPiece = self.getPieceAtPosition(translated[0], translated[1])
                    if(not obstructingPiece is None):
                        if(obstructingPiece.pieceColor == enemyColor):
                            visionFiles.append(translated[0])
                            visionRanks.append(translated[1])
                            takes.append(True)
                    
                        break
                        
                    else:
                        visionFiles.append(translated[0])
                        visionRanks.append(translated[1])
                        takes.append(False)

            for i in range(1,8):
                index1 = matrixCoords[0] - i
                index2 =  matrixCoords[1] - i
                if(index1 >= 0 and index2 >= 0):
                    translated = translator.getChessNotationCoordinates(index1, index2)
                    obstructingPiece = self.getPieceAtPosition(translated[0], translated[1])
                    if(not obstructingPiece is None):
                        if(obstructingPiece.pieceColor == enemyColor):
                            visionFiles.append(translated[0])
                            visionRanks.append(translated[1])
                            takes.append(True)
                    
                        break
                        
                    else:
                        visionFiles.append(translated[0])
                        visionRanks.append(translated[1])
                        takes.append(False)
            
        elif(pieceType == PieceType.ROOK):
                #This is kind of the same case but we explore columns and rows
                #Let's do some copy paste and modify to our needs
            for i in range(1,8):
                index1 = matrixCoords[0]
                index2 = matrixCoords[1] + i
                if(index2 <= 7):
                    translated = translator.getChessNotationCoordinates(index1, index2)
                    obstructingPiece = self.getPieceAtPosition(translated[0], translated[1])
                    if(not obstructingPiece is None):
                        if(obstructingPiece.pieceColor == enemyColor):
                            visionFiles.append(translated[0])
                            visionRanks.append(translated[1])
                            takes.append(True)
                    
                        break
                        
                    else:
                        visionFiles.append(translated[0])
                        visionRanks.append(translated[1])
                        takes.append(False)

            for i in range(1,8):
                index1 = matrixCoords[0]
                index2 =  matrixCoords[1] - i
                if(index2 >= 0):
                    translated = translator.getChessNotationCoordinates(index1, index2)
                    obstructingPiece = self.getPieceAtPosition(translated[0], translated[1])
                    if(not obstructingPiece is None):
                        if(obstructingPiece.pieceColor == enemyColor):
                            visionFiles.append(translated[0])
                            visionRanks.append(translated[1])
                            takes.append(True)
                    
                        break
                        
                    else:
                        visionFiles.append(translated[0])
                        visionRanks.append(translated[1])
                        takes.append(False)
                        
            for i in range(1,8):
                index1 = matrixCoords[0] + i
                index2 =  matrixCoords[1]
                if(index1 <= 7):
                    translated = translator.getChessNotationCoordinates(index1, index2)
                    obstructingPiece = self.getPieceAtPosition(translated[0], translated[1])
                    if(not obstructingPiece is None):
                        if(obstructingPiece.pieceColor == enemyColor):
                            visionFiles.append(translated[0])
                            visionRanks.append(translated[1])
                            takes.append(True)
                    
                        break
                        
                    else:
                        visionFiles.append(translated[0])
                        visionRanks.append(translated[1])
                        takes.append(False)

            for i in range(1,8):
                index1 = matrixCoords[0] - i
                index2 =  matrixCoords[1]
                if(index1 >= 0):
                    translated = translator.getChessNotationCoordinates(index1, index2)
                    obstructingPiece = self.getPieceAtPosition(translated[0], translated[1])
                    if(not obstructingPiece is None):
                        if(obstructingPiece.pieceColor == enemyColor):
                            visionFiles.append(translated[0])
                            visionRanks.append(translated[1])
                            takes.append(True)
                    
                        break
                        
                    else:
                        visionFiles.append(translated[0])
                        visionRanks.append(translated[1])
                        takes.append(False)
            
            #The queen is just a combination of rook + bishop, 
        elif(pieceType == PieceType.QUEEN):
                #Diagonals 
            for i in range(1,8):
                index1 = matrixCoords[0] - i
                index2 = matrixCoords[1] + i
                if(index1 >= 0 and index2 <= 7):
                    translated = translator.getChessNotationCoordinates(index1, index2)
                    obstructingPiece = self.getPieceAtPosition(translated[0], translated[1])
                    if(not obstructingPiece is None):
                        if(obstructingPiece.pieceColor == enemyColor):
                            visionFiles.append(translated[0])
                            visionRanks.append(translated[1])
                            takes.append(True)
                    
                        break
                        
                    else:
                        visionFiles.append(translated[0])
                        visionRanks.append(translated[1])
                        takes.append(False)

            for i in range(1,8):
                index1 = matrixCoords[0] + i
                index2 =  matrixCoords[1] - i
                if(index1 <= 7 and index2 >= 0):
                    translated = translator.getChessNotationCoordinates(index1, index2)
                    obstructingPiece = self.getPieceAtPosition(translated[0], translated[1])
                    if(not obstructingPiece is None):
                        if(obstructingPiece.pieceColor == enemyColor):
                            visionFiles.append(translated[0])
                            visionRanks.append(translated[1])
                            takes.append(True)
                    
                        break
                        
                    else:
                        visionFiles.append(translated[0])
                        visionRanks.append(translated[1])
                        takes.append(False)
                        
            for i in range(1,8):
                index1 = matrixCoords[0] + i
                index2 =  matrixCoords[1] + i
                if(index1 <= 7 and index2 <= 7):
                    translated = translator.getChessNotationCoordinates(index1, index2)
                    obstructingPiece = self.getPieceAtPosition(translated[0], translated[1])
                    if(not obstructingPiece is None):
                        if(obstructingPiece.pieceColor == enemyColor):
                            visionFiles.append(translated[0])
                            visionRanks.append(translated[1])
                            takes.append(True)
                    
                        break
                        
                    else:
                        visionFiles.append(translated[0])
                        visionRanks.append(translated[1])
                        takes.append(False)

            for i in range(1,8):
                index1 = matrixCoords[0] - i
                index2 =  matrixCoords[1] - i
                if(index1 >= 0 and index2 >= 0):
                    translated = translator.getChessNotationCoordinates(index1, index2)
                    obstructingPiece = self.getPieceAtPosition(translated[0], translated[1])
                    if(not obstructingPiece is None):
                        if(obstructingPiece.pieceColor == enemyColor):
                            visionFiles.append(translated[0])
                            visionRanks.append(translated[1])
                            takes.append(True)
                    
                        break
                        
                    else:
                        visionFiles.append(translated[0])
                        visionRanks.append(translated[1])
                        takes.append(False)
                        
            for i in range(1,8):
                index1 = matrixCoords[0]
                index2 = matrixCoords[1] + i
                if(index2 <= 7):
                    translated = translator.getChessNotationCoordinates(index1, index2)
                    obstructingPiece = self.getPieceAtPosition(translated[0], translated[1])
                    if(not obstructingPiece is None):
                        if(obstructingPiece.pieceColor == enemyColor):
                            visionFiles.append(translated[0])
                            visionRanks.append(translated[1])
                            takes.append(True)
                    
                        break
                        
                    else:
                        visionFiles.append(translated[0])
                        visionRanks.append(translated[1])
                        takes.append(False)

            for i in range(1,8):
                index1 = matrixCoords[0]
                index2 =  matrixCoords[1] - i
                if(index2 >= 0):
                    translated = translator.getChessNotationCoordinates(index1, index2)
                    obstructingPiece = self.getPieceAtPosition(translated[0], translated[1])
                    if(not obstructingPiece is None):
                        if(obstructingPiece.pieceColor == enemyColor):
                            visionFiles.append(translated[0])
                            visionRanks.append(translated[1])
                            takes.append(True)
                    
                        break
                        
                    else:
                        visionFiles.append(translated[0])
                        visionRanks.append(translated[1])
                        takes.append(False)
                        
            for i in range(1,8):
                index1 = matrixCoords[0] + i
                index2 =  matrixCoords[1]
                if(index1 <= 7):
                    translated = translator.getChessNotationCoordinates(index1, index2)
                    obstructingPiece = self.getPieceAtPosition(translated[0], translated[1])
                    if(not obstructingPiece is None):
                        if(obstructingPiece.pieceColor == enemyColor):
                            visionFiles.append(translated[0])
                            visionRanks.append(translated[1])
                            takes.append(True)
                    
                        break
                        
                    else:
                        visionFiles.append(translated[0])
                        visionRanks.append(translated[1])
                        takes.append(False)

            for i in range(1,8):
                index1 = matrixCoords[0] - i
                index2 =  matrixCoords[1]
                if(index1 >= 0):
                    translated = translator.getChessNotationCoordinates(index1, index2)
                    obstructingPiece = self.getPieceAtPosition(translated[0], translated[1])
                    if(not obstructingPiece is None):
                        if(obstructingPiece.pieceColor == enemyColor):
                            visionFiles.append(translated[0])
                            visionRanks.append(translated[1])
                            takes.append(True)
                    
                        break
                        
                    else:
                        visionFiles.append(translated[0])
                        visionRanks.append(translated[1])
                        takes.append(False)
            
        
        elif(pieceType == PieceType.KNIGHT):
            #Knighs move in an L shape. 
            for i in [-2,2]:
                index1 = matrixCoords[0]+i
                for j in [-1,1]:
                    index2 = matrixCoords[1] + j
                    
                    if(index1 >= 0 and index1 <= 7 and index2 >= 0 and index2 <= 7):
                        translated = translator.getChessNotationCoordinates(index1, index2)
                        obstructingPiece = self.getPieceAtPosition(translated[0], translated[1])
                        if(not obstructingPiece is None):
                            if(obstructingPiece.pieceColor == enemyColor):
                                visionFiles.append(translated[0])
                                visionRanks.append(translated[1])
                                takes.append(True)
                        
                        else:
                            visionFiles.append(translated[0])
                            visionRanks.append(translated[1])
                            takes.append(False)
            
            for i in [-2,2]:
                index2 = matrixCoords[1]+i
                for j in [-1,1]:
                    index1 = matrixCoords[0] + j
                    if(index1 >= 0 and index1 <= 7 and index2 >= 0 and index2 <= 7):
                        translated = translator.getChessNotationCoordinates(index1, index2)
                        obstructingPiece = self.getPieceAtPosition(translated[0], translated[1])
                        if(not obstructingPiece is None):
                            if(obstructingPiece.pieceColor == enemyColor):
                                visionFiles.append(translated[0])
                                visionRanks.append(translated[1])
                                takes.append(True)
                        
                        else:
                            visionFiles.append(translated[0])
                            visionRanks.append(translated[1])
                            takes.append(False)
            
        
        elif(pieceType == PieceType.KING):
            
            for i in range(-1,2):
                for j in range(-1,2):
                    if(i!= 0 or j != 0):
                        index1 = matrixCoords[0] + i
                        index2 = matrixCoords[1] + j
                        
                        if(index1 >= 0 and index1 <= 7 and index2 >= 0 and index2 <= 7):
                            translated = translator.getChessNotationCoordinates(index1, index2)
                            obstructingPiece = self.getPieceAtPosition(translated[0], translated[1])
                            if(not obstructingPiece is None):
                                if(obstructingPiece.pieceColor == enemyColor):
                                    visionFiles.append(translated[0])
                                    visionRanks.append(translated[1])
                                    takes.append(True)
                        
                            else:
                                visionFiles.append(translated[0])
                                visionRanks.append(translated[1])
                                takes.append(False)
            
            
            rook1 = self.getPieceAtPosition("h", rank)
            rook2 = self.getPieceAtPosition("a", rank)
            if(not rook1 is None and rook1.pieceColor == pieceColor and rook1.moveCounter == 0 and pieceMoveCounter == 0 and not self.isOccupied("f", rank) and not self.isOccupied("g", rank)):
                visionFiles.append("g")
                visionRanks.append(rank)
                takes.append(False)
            
            
            if(not rook2 is None and rook2.pieceColor == pieceColor and rook2.moveCounter == 0 and pieceMoveCounter == 0 and not self.isOccupied("b", rank) and not self.isOccupied("c", rank) and not self.isOccupied("d", rank)):
                visionFiles.append("c")
                visionRanks.append(rank)
                takes.append(False)
        return visionFiles, visionRanks, takes
                
    def isDestinationSquareShared(self, refPiece, pieceType, pieceColor, file, rank):
        for i in range(0,len(self.pieces)):
            piece = self.pieces[i]
            if(refPiece != piece and piece.pieceColor == pieceColor and piece.pieceType == pieceType):
                moves = piece.getPieceMoves()
                for j in range(0,len(moves)):
                    move = moves[j]
                    destination = move.getPieceFinalPosition()
                    if(destination[0] == file and destination[1] == rank):
                        return True, piece.file, piece.rank, move
        return False, "", "", None
    
    
    def removePiece(self, file, rank, pieceColor):
        for i in range(0,len(self.pieces)):
            if(self.pieces[i].pieceColor == pieceColor and self.pieces[i].file == file and self.pieces[i].rank == rank):
                self.pieces.pop(i)
                break
                
    
    def initializeBoard(self):
        #White pawns and black pawns
        files = ["a","b","c", "d", "e", "f","g", "h"]
        for i in range(0,8):
            self.addPiece(PieceType.PAWN, PieceColor.BLACK, files[i],"7")
            self.addPiece(PieceType.PAWN, PieceColor.WHITE, files[i], "2")
        
        for i in ["a", "h"]:
            self.addPiece(PieceType.ROOK, PieceColor.BLACK, i,"8")
            self.addPiece(PieceType.ROOK, PieceColor.WHITE, i, "1")
        
        for i in ["b", "g"]:
            self.addPiece(PieceType.KNIGHT, PieceColor.BLACK, i,"8")
            self.addPiece(PieceType.KNIGHT, PieceColor.WHITE, i, "1")
            
        for i in ["c", "f"]:
            self.addPiece(PieceType.BISHOP, PieceColor.BLACK, i,"8")
            self.addPiece(PieceType.BISHOP, PieceColor.WHITE, i, "1")

        self.addPiece(PieceType.QUEEN, PieceColor.BLACK, "d","8")
        self.addPiece(PieceType.QUEEN, PieceColor.WHITE, "d", "1")
        
        self.addPiece(PieceType.KING, PieceColor.BLACK, "e","8")
        self.addPiece(PieceType.KING, PieceColor.WHITE, "e", "1")
        
        self.updateMoves(False, False)
        
    def updateMoves(self, check, checkMate):
        for i in range(0,len(self.pieces)):
            self.pieces[i].resetPieceMoves()
            
            
        for i in range(0,len(self.pieces)):
            self.pieces[i].computePieceMoves(self, check,checkMate)
        
        
    
    def makeMove(self, moveString):
        pieceColorToMove = PieceColor(self.moveNumber % 2)
        madeMove = False
        check = False
        checkmate = False
        takes = False
        removed = []
        for i in range(0,len(self.pieces)):
            piece = self.pieces[i]
            pieceMoves = piece.getPieceMoves()
            move = ChessMove(moveString)
            if(move in pieceMoves and piece.pieceColor == pieceColorToMove):
                takes, check, checkmate = move.executeMove(piece)
                if(len(self.executedMoves) <= self.moveNumber):
                    self.executedMoves.append(move)
                if(takes):
                    takenPosition = move.getPieceFinalPosition()
                    #En passant is a dumbo case which should not exist. 
                    if(piece.pieceType == PieceType.PAWN and (piece.rank == "4" or piece.rank == "5") and self.getPieceAtPosition(takenPosition[0], takenPosition[1]) is None):
                        color = PieceColor((self.moveNumber + 1)%2)
                        if(color == PieceColor.WHITE):
                            removed.append([takenPosition[0],str(int(takenPosition[1]) - 1), color])
                        else:
                            removed.append([takenPosition[0],str(int(takenPosition[1]) + 1), color])
                        
                    else:
                        removed.append([takenPosition[0], takenPosition[1], PieceColor((self.moveNumber + 1)%2)])
                
                madeMove = True
                    
        for i in range(0,len(removed)):
            removeParams = removed[i]
            self.removePiece(removeParams[0], removeParams[1], removeParams[2])
        
        if(not madeMove):
            if(not self.gameEnded):
                print("Invalid move")
                return -1
            else:
                print("Game ended")
        else:
            if(checkmate):
                self.gameEnded = True
                self.winner = pieceColorToMove
                if(pieceColorToMove == PieceColor.WHITE):
                    print("White wins!")
                else:
                    print("Black wins!")
            
            #If a move was made recompute the available moves for each piece
            for i in range(0,len(self.pieces)):
                if(self.pieces[i].pieceColor != pieceColorToMove):
                    self.pieces[i].resetPieceMoves()
            
            for i in range(0,len(self.pieces)):
                if(self.pieces[i].pieceColor != pieceColorToMove):
                    self.pieces[i].computePieceMoves(self, check, checkmate)
            
            self.moveNumber = self.moveNumber + 1
            
    
    def getNMoves(self, pieceColor):
        nMoves = 0
        for i in range(0,len(self.pieces)):
            if(self.pieces[i].pieceColor == pieceColor):
                nMoves = nMoves + len(self.pieces[i].pieceMoves)
        
        return nMoves
        
        
            
        
    def drawBoard(self):
        fig, ax = plt.subplots(figsize = (4,4))
        for i in range(0,8):
            for j in range(0,8):
                if((i%2 == 0 and j%2 == 1) or (i%2 == 1 and j%2 == 0)):
                    ax.add_patch(Rectangle((i,j), 1,1, facecolor = self.whiteColor, fill = True, edgecolor = "none"))
                else:
                    ax.add_patch(Rectangle((i,j),1,1,facecolor = self.blackColor, fill = True, edgecolor = "none"))
        coordTranslator = ChessCoordinateTranslator()
        pieceRenderer = PieceImageRenderer("PieceImages")
        for i in range(0,len(self.pieces)):
            piece = self.pieces[i]
            pieceimage = pieceRenderer.getPieceImage(200,200, piece.pieceType, piece.pieceColor)
            imageBox = OffsetImage(pieceimage, zoom = 0.15)
            pieceCoordinates = coordTranslator.getImageCoordinates(piece.file, piece.rank)
            
            annotationBox = AnnotationBbox(imageBox, (pieceCoordinates[1]+0.5,pieceCoordinates[0]+0.5), frameon = False)
            ax.add_artist(annotationBox)
        
        ticksArray = ["a","b","c","d","e","f","g","h"]
        ticksPositions = np.arange(0.5,8,1)
        ticksArray2 = np.arange(1,9,1)
        ax.set_xticks(ticksPositions)
        ax.set_xticklabels(ticksArray)
        ax.set_yticks(ticksPositions)
        ax.set_yticklabels(ticksArray2)
        ax.set_xlim([0,8])
        ax.set_ylim([0,8])