import matplotlib.pyplot as plt
import numpy as np
from ChessGame import ChessCoordinateTranslator


class ChessConnection:

    def __init__(self, fromFile, fromRank, toFile, toRank, weight):
        self.fromSquare = fromFile + fromRank
        self.toSquare = toFile + toRank
        self.weight = weight

    def getFromFile(self):
        return self.fromSquare[0]

    def getFromRank(self):
        return self.fromSquare[1]

    def getToFile(self):
        return self.toSquare[0]

    def getToRank(self):
        return self.toSquare[1]

    def __eq__(self, other):
        return self.fromSquare == other.fromSquare and self.toSquare == other.toSquare

class ChessNode:
    def __init__(self, file, rank):
        self.file = file
        self.rank = rank

    def __eq__(self, other):
        return self.file == other.file and self.rank == other.rank

    def getId(self):
        return self.file + self.rank
    

class ChessGraph:
    
    def __init__(self, board, filterColor, color):
        self.board = board
        self.nodes = []
        self.connections = {}
        self.createGraph(filterColor, color)

    def createGraph(self, filterColor, color):
        pieces = self.board.pieces
        nPieces = len(pieces)

        fileNames = ["a", "b", "c", "d", "e", "f", "g", "h"]
        rankNames = ["1", "2", "3", "4", "5", "6", "7", "8"]

        for i in range(0, len(fileNames)):
            for j in range(0,len(rankNames)):
                file = fileNames[i]
                rank = rankNames[j]
                node = ChessNode(file, rank)
                self.addNode(node)
                

        if(filterColor):
            for i in range(0,nPieces):
                piece = pieces[i]
                if(piece.pieceColor == color):
                    files, ranks, takes = self.board.getPieceBoardVision(piece.pieceType, piece.file, piece.rank, piece.moveCounter, piece.pieceColor)
                    rank = piece.rank
                    file = piece.file
                    for j in range(0,len(files)):
                        self.addConnection(file, rank, files[j], ranks[j])
            
        else:
            for i in range(0,nPieces):
                piece = pieces[i]
                files, ranks, takes = self.board.getPieceBoardVision(piece.pieceType, piece.file, piece.rank, piece.moveCounter, piece.pieceColor)
                rank = piece.rank
                file = piece.file
                for j in range(0,len(files)):
                    self.addConnection(file, rank, files[j], ranks[j])


    def addNode(self, node):
        if(not node in self.nodes):
            self.nodes.append(node)
            self.connections[node.getId()] = []

    def getNodeById(self, nodeId):
        file = nodeId[0]
        rank = nodeId[1]
        nNodes = len(self.nodes)
        
        for i in range(0,nNodes):
            node = self.nodes[i]
            if(file == node.file and rank == node.rank):
                return node
        
        return -1

    def addConnection(self, fromFile, fromRank, toFile, toRank):

        nodeId = fromFile + fromRank

        #Connections will have a weight of 1
        connection = ChessConnection(fromFile, fromRank, toFile, toRank, 1)
        if (not connection in self.connections[nodeId]):
            self.connections[nodeId].append(connection)

    def drawGraph(self):
        plt.figure(figsize = (4,4))
        #Draw the connections 
        connections = self.getAllConnections()
        nConnections = len(connections)
        coordTranslator = ChessCoordinateTranslator()
        connectionColor = ""

        for i in range(0,nConnections):
            connection = connections[i]
            fromFile = connection.getFromFile()
            fromRank = connection.getFromRank()
            toFile = connection.getToFile()
            toRank = connection.getToRank()

            [fromY, fromX] = coordTranslator.getImageCoordinates(fromFile, fromRank)
            [toY, toX] = coordTranslator.getImageCoordinates(toFile, toRank)

            plt.plot([fromX, toX], [fromY, toY], marker = "none", linewidth = 2, color = "#37a7ed")
        
        #Let's draw the nodes
        nodeColor = "#c95e20"
        nNodes = len(self.nodes)
        
        for i in range(0,nNodes):
            node = self.nodes[i]
            file = node.file
            rank = node.rank
            [yPos,xPos] = coordTranslator.getImageCoordinates(file,rank)
            plt.plot([xPos], [yPos], marker = "o", markersize = 5, color = nodeColor)

    def getAllConnections(self):
        nNodes = len(self.nodes)
        connections = []
        for i in range(0,nNodes):
            node = self.nodes[i]
            nodeId = node.getId()
            connections.extend(self.connections[nodeId])

        return connections


    def getAverageDegree(self):
        avgDegree = 0
        for i in range(0,len(self.nodes)):
            node = self.nodes[i]
            nodeId = node.getId()
            degree = len(self.connections[nodeId])
            avgDegree = avgDegree + degree/len(self.nodes)


        return avgDegree
            
            
            
        
        

        
        


        

        