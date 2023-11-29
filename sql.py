import streamlit as st
import pandas as pd

from antlr4 import *
from sqlinterpreterLexer import sqlinterpreterLexer
from sqlinterpreterParser import sqlinterpreterParser
from sqlinterpreterVisitor import sqlinterpreterVisitor

class evalVisitor(sqlinterpreterVisitor):
    def __init__(self):
        self.currentState = None
        self.mapOrder = {'asc':True, 'desc': False}

    def visitRoot(self, ctx:sqlinterpreterParser.RootContext):
        return self.visit(ctx.consulta())
    
    def visitConsulta(self, ctx:sqlinterpreterParser.ConsultaContext):
        self.visit(ctx.selection())
        return self.currentState
    

    def visitSelection(self, ctx:sqlinterpreterParser.SelectionContext):
        self.visit(ctx.tables())
        self.visit(ctx.campos())
        if(ctx.order()):
            self.visit(ctx.order())

    def visitOrder(self, ctx:sqlinterpreterParser.OrderContext):
        nodes = ctx.preferencia()
        names = []
        ascending= []
        for i in nodes:
            name, prefe = self.visit(i)
            names.append(name)
            ascending.append(prefe)
        self.currentState = self.currentState.sort_values(by=names, ascending=ascending)
    
    def visitPreferencia(self, ctx:sqlinterpreterParser.PreferenciaContext):
        name = ctx.NAME().getText()
        order = True
        if ctx.op :
            print(ctx.op)
            label = ctx.op.text
            order= self.mapOrder[label]
        return name, order



    
    def visitTables(self, ctx:sqlinterpreterParser.TablesContext):
        tabla = ctx.NAME().getText()

        path = "./tablas/"
        path = path + tabla + ".csv"
        df = pd.read_csv(path)
        
        self.currentState = df
    def visitCampos(self, ctx:sqlinterpreterParser.CamposContext):
       nodes = ctx.campo()
       lista = []
       for i in nodes:
           lista.append(self.visit(i))
       self.currentState = pd.concat(lista, axis=1)


    def visitCampo(self, ctx:sqlinterpreterParser.CampoContext):
        columna = self.visit(ctx.campo2())
        if(ctx.AS()):
            new_col = ctx.NAME().getText()
            columna = columna.rename(new_col)
        return columna
    
    def visitSumMinus(self, ctx:sqlinterpreterParser.SumMinusContext):
        [node0,_,node1] = list(ctx.getChildren())
        node0 = self.visit(node0)
        node1 = self.visit(node1)
        if(ctx.SUMA()):
            return node0 + node1
        else:
            return node0 - node1
    
    def visitParetesis(self, ctx:sqlinterpreterParser.ParetesisContext):
        return self.visit(ctx.campo2())
    def visitMulDiv(self, ctx:sqlinterpreterParser.MulDivContext):
        [node0,_,node1] = list(ctx.getChildren())
        node0 = self.visit(node0)
        node1 = self.visit(node1)
        if(ctx.MUL()):
            return node0 * node1
        else:
            return node0 / node1
    def visitNum(self, ctx:sqlinterpreterParser.NumContext):
        num = ctx.NUM().getText()
        return float(num)
    
    def visitColumn(self, ctx:sqlinterpreterParser.ColumnContext):
        nombre = ctx.nombre.text
        if nombre!= "*":
            return self.currentState[nombre]
        return self.currentState
        
title = st.text_input("Query:")

button = st.button("Submit")

if button:
    input_stream = InputStream(title)
    lexer = sqlinterpreterLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = sqlinterpreterParser(token_stream)
   
    tree = parser.root()
   ## print(parser.getNumberOfSyntaxErrors(), 'errors de sintaxi.')
   ## print(tree.toStringTree(recog=parser))
    if parser.getNumberOfSyntaxErrors() == 0:
        visitor = evalVisitor()
        df = visitor.visit(tree)
        st.table(df)