import sys


class Todot:
    def __init__(self, file):
        self.ctp = 0
        self.dot = open(file[0:-5] + ".dot", "w")

    def dotInt(self, succ, val, label=''):
        self.ctp += 1
        self.dot.write(f"""
        n{self.ctp} [label=\"{val}\"];
        {succ} -- n{self.ctp}[label="{label}"]
        """)

    def dotStr(self, succ, val, label=''):
        self.ctp += 1
        self.dot.write(f"""
        n{self.ctp} [label={val}];
        {succ} -- n{self.ctp}[label="{label}"]
        """)

    def dotDict(self, pred, val, label=''):
        self.ctp += 1
        l = f'n{self.ctp}'
        if 'type' in val:
            labelnode = val['type']
        else:
            labelnode='dict'
        self.dot.write(f"""
        {l} [shape=\"invhouse\",label="{labelnode}"];
        {pred} -- {l} [label="{label}"];
        """)
        for v in val:
            if v not in {'type','col','line'}:
                self.dotAny(l, val[v], v)

    def dotList(self, pred, val, label=''):
        self.ctp += 1
        l = f'n{self.ctp}'
        self.dot.write(f"""
        {l} [shape=\"point\",label=\"\"];
        {pred} -- {l} [label="{label}"];
        """)
        for v in val:
            self.dotAny(l, v)

    def dotAny(self, pred, val, label=''):
        if type(val) == type({}):
            self.dotDict(pred, val, label)
        elif type(val) == type([]):
            self.dotList(pred, val, label)
        elif type(val) == type(""):
            self.dotStr(pred, val, label)
        else:
            self.dotInt(pred, val, label)

    def todot(self,val):
        self.dot.write("""
        graph mygraph {
        n0 [shape=point] ;
        """)
        self.dotAny('n0', val)
        self.dot.write('''}
        ''')


if __name__ == "__main__":
    file = sys.argv[1]
    print('-----debut')
    todot = Todot(file)
    todot.todot({'type':'good','a':[5,8,0,2,[8,1,2,3,4]],'b':[[8,9,76,4],'toto'],'c':[[8,9,76,4],'tutu']})
    print('-----fin')
