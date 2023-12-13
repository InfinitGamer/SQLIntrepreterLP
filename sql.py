import streamlit as st
import pandas as pd

from antlr4 import *
from sqlinterpreterLexer import sqlinterpreterLexer
from sqlinterpreterParser import sqlinterpreterParser
from sqlinterpreterVisitor import sqlinterpreterVisitor
import operator as op


class evalVisitor(sqlinterpreterVisitor):
    def __init__(self):

        # because SQL during order by can access the original table and the
        # table of select. We will have the same thing but in a unique table.
        self.tableForOrder = None
        self.currentState = None
        self.mapOrder = {'asc': True, 'desc': False}
        self.mapBoolean = {
            '=': op.eq,
            '!=': op.ne,
            '<': op.lt,
            '<=': op.le,
            '>': op.gt,
            '>=': op.ge,
            'not': op.neg,
            'and': lambda x, y: x & y,
            'or': lambda x, y: x | y
        }

    def visitRoot(self, ctx: sqlinterpreterParser.RootContext):
        return self.visit(ctx.consulta())

    def visitConsulta(self, ctx: sqlinterpreterParser.ConsultaContext):
        self.visit(ctx.selection())
        st.table(self.currentState)

    def visitSelection(self, ctx: sqlinterpreterParser.SelectionContext):
        self.visit(ctx.tables())
        if (ctx.where()):
            self.visit(ctx.where())

        self.visit(ctx.campos())

        if (ctx.order()):
            self.visit(ctx.order())

    def visitOrder(self, ctx: sqlinterpreterParser.OrderContext):
        nodes = ctx.preferencia()
        names = []
        ascending = []
        for i in nodes:
            name, prefe = self.visit(i)
            names.append(name)
            ascending.append(prefe)
        self.tableForOrder = self.tableForOrder.sort_values(
            by=names, ascending=ascending)
        self.currentState = self.currentState.reindex(self.tableForOrder.index)

    def visitPreferencia(self, ctx: sqlinterpreterParser.PreferenciaContext):
        name = ctx.NAME().getText()
        order = True
        if ctx.op:
            label = ctx.op.text
            order = self.mapOrder[label]
        return name, order

    def visitWhere(self, ctx: sqlinterpreterParser.WhereContext):
        cond = self.visit(ctx.condition())

        self.currentState = self.currentState.loc[cond]
        self.tableForOrder = self.currentState.copy()

    def visitNot(self, ctx: sqlinterpreterParser.NotContext):
        return ~self.visit(ctx.condition())

    def visitParetesis2(self, ctx: sqlinterpreterParser.Paretesis2Context):
        return self.visit(ctx.condition())

    def visitColumna(self, ctx: sqlinterpreterParser.ColumnaContext):
        return self.visit(ctx.campo2())

    def visitBooleanCondition(
            self,
            ctx: sqlinterpreterParser.BooleanConditionContext):
        cond1 = self.visit(ctx.condition(0))
        cond2 = self.visit(ctx.condition(1))
        op = ctx.op.text
        cond = self.mapBoolean[op](cond1, cond2)
        return cond

    def visitString(self, ctx: sqlinterpreterParser.StringContext):
        return ctx.NAME().getText()

    def visitTable(self, ctx: sqlinterpreterParser.TableContext):
        tabla = ctx.NAME().getText()

        path = "./tablas/"
        path = path + tabla + ".csv"
        df = pd.read_csv(path)
        return df

    def visitTables(self, ctx: sqlinterpreterParser.TablesContext):
        df = self.visit(ctx.table())

        self.currentState = df
        self.tableForOrder = df.copy()
        if (ctx.inner()):
            self.visit(ctx.inner())

    def visitInner(self, ctx: sqlinterpreterParser.InnerContext):
        second_table = self.visit(ctx.table())
        name1 = ctx.NAME(0).getText()
        name2 = ctx.NAME(1).getText()
        self.currentState = self.currentState.merge(
            second_table, left_on=name1, right_on=name2, how='inner')
        self.tableForOrder = self.currentState.copy()
        if (ctx.inner()):
            self.visit(ctx.inner())

    def visitCampos(self, ctx: sqlinterpreterParser.CamposContext):
        nodes = ctx.campo()
        lista = []
        for i in nodes:
            lista.append(self.visit(i))
        self.currentState = pd.concat(lista, axis=1)

        # we create a table for ordering that is the combination of the original table (with columns that are might get altered during selection)
        # and the new created ones
        # this part of code does this thing, update the existing ones and
        # concadente the new ones.
        common_columns = self.currentState.columns.intersection(
            self.tableForOrder.columns)
        self.tableForOrder[common_columns] = self.currentState[common_columns]
        self.tableForOrder = pd.concat([self.currentState,
                                        self.tableForOrder.loc[:,
                                                               ~self.tableForOrder.columns.isin(self.currentState.columns)]],
                                       axis=1)

    def visitCampo(self, ctx: sqlinterpreterParser.CampoContext):
        columna = self.visit(ctx.campo2())
        if (ctx.AS()):
            new_col = ctx.NAME().getText()
            columna = columna.rename(new_col)
        return columna

    def visitMinus(self, ctx: sqlinterpreterParser.MinusContext):
        valor = self.visit(ctx.campo2())
        return -1 * valor

    def visitSumMinus(self, ctx: sqlinterpreterParser.SumMinusContext):
        [node0, _, node1] = list(ctx.getChildren())
        node0 = self.visit(node0)
        node1 = self.visit(node1)
        if (ctx.SUMA()):
            return node0 + node1
        else:
            return node0 - node1

    def visitParetesis(self, ctx: sqlinterpreterParser.ParetesisContext):
        return self.visit(ctx.campo2())

    def visitNumero(self, ctx: sqlinterpreterParser.NumeroContext):
        return self.visit(ctx.num())

    def visitMulDiv(self, ctx: sqlinterpreterParser.MulDivContext):
        [node0, _, node1] = list(ctx.getChildren())
        node0 = self.visit(node0)
        node1 = self.visit(node1)
        if (ctx.MUL()):
            return node0 * node1
        else:
            return node0 / node1

    def visitNum(self, ctx: sqlinterpreterParser.NumContext):
        num = ctx.NUM().getText()
        num = float(num)
        if (ctx.op):
            if (ctx.op.text == "-"):
                num *= -1.0
        return num

    def visitColumn(self, ctx: sqlinterpreterParser.ColumnContext):
        nombre = ctx.nombre.text
        if nombre != "*":
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
   # print(parser.getNumberOfSyntaxErrors(), 'errors de sintaxi.')
   # print(tree.toStringTree(recog=parser))
    if parser.getNumberOfSyntaxErrors() == 0:
        visitor = evalVisitor()
        df = visitor.visit(tree)
