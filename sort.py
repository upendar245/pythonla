#!/usr/bin/python
""" Parses sudo files """

import re,sys

class SudoCmnd:
    def __init__(self,runas,command):
        self.runas = runas.strip()
        self.command = command.strip()

    def __repr__(self):
        if self.runas != "":
            return "(%s) %s" % (self.runas, self.command)
        else:
            return self.command

class SudoRule:
    def __init__(self,user,server,command,name):
        self.user = user
        self.server = server
        self.command = command
        self.name = name

    def __repr__(self):
        return "# NAME=%s\n%s\t%s=%s" % (self.name,self.user,self.server,self.command)

class SudoersParser:
    def __init__(self):
        self.hostAliases  = {}
        self.userAliases  = {}
        self.cmndAliases  = {}
        self.runasAliases  = {}
        self.rules        = []
        self.defaultsLines = []
        self.commentLines = []

    def parseFile(self,f):
        with open(f,"r") as fh:
            lines = fh.readlines()
        lines = self._collapseLines(lines)

        defaultsRE  = re.compile(r"^\s*Defaults")
        hostAliasRE = re.compile(r"^\s*Host_Alias")
        userAliasRE = re.compile(r"^\s*User_Alias")
        runasAliasRE = re.compile(r"^\s*Runas_Alias")
        cmndAliasRE = re.compile(r"^\s*Cmnd_Alias")
        commentRE = re.compile(r"^\s*#")
        ruleRE = re.compile(r"^\s*#\s*NAME=")

        for idx, line in enumerate(lines):
            if not commentRE.search(line):
                break

        self.commentLines = lines[0:idx]
        restOfFile = lines[idx:]
        errorString = ""
        for rest_idx, line in enumerate(restOfFile):
            if(defaultsRE.search(line)):
                self.defaultsLines.append(line)
                continue
            if(hostAliasRE.search(line)):
                self.hostAliases.update(self._parseAlias(line,"Host_Alias"))
                continue
            if(userAliasRE.search(line)):
                self.userAliases.update(self._parseAlias(line,"User_Alias"))
                continue
            if(runasAliasRE.search(line)):
                self.runasAliases.update(self._parseAlias(line,"Runas_Alias"))
                continue
            if(cmndAliasRE.search(line)):
                self.cmndAliases.update(self._parseAlias(line,"Cmnd_Alias"))
                continue
            if len(line.strip()) != 0 and not ruleRE.search(line):
                rule = self._parseRule(line, restOfFile[rest_idx-1])  # pass previous line because it should be a comment for the name of this rule
                if(rule):
                    self.rules.append(rule)
                else:
                    errorString += "Bad Rule: %sDid you remember to use the comment/rule syntax pair?\n" % (line)

        return errorString

    def outputFile(self, filename):
        # Sort the host aliases by alias name
        host_aliases_tuple_list = sorted(self.hostAliases.items())
        # sort the user aliases by alias name
        user_aliases_kv_list = sorted(self.userAliases.items())
        # sort the runas asliases by alias name
        runas_aliases_kv_list =  sorted(self.runasAliases.items())
        # sort the command aliases by alias name
        cmnd_aliases_kv_list =  sorted(self.cmndAliases.items())

        # sort the rules by the NAME=x field in their comment string.
        rules_list = sorted(self.rules, key=lambda x: x.name)

        with open(filename, "w") as fh:
            for x in self.commentLines:
                fh.write(x)

            for x in self.defaultsLines:
                fh.write(x)

            fh.write("\n")

            for x in host_aliases_tuple_list:
                fh.write("Host_Alias\t"+x[0]+"="+", ".join(x[1])+"\n")

            fh.write("\n")

            for x in user_aliases_kv_list:
                fh.write("User_Alias\t"+x[0]+"="+", ".join(x[1])+"\n")

            fh.write("\n")

            for x in runas_aliases_kv_list:
                fh.write("Runas_Alias\t"+x[0]+"="+", ".join(x[1])+"\n")

            fh.write("\n")

            for x in cmnd_aliases_kv_list:
                fh.write("Cmnd_Alias\t"+x[0]+"="+x[1][0])
                if len(x[1]) > 1:
                    fh.write(", \\\n\t\t\t")
                    fh.write(", \\\n\t\t\t".join(x[1][1:]))
                fh.write("\n")

            for rule in rules_list:
                fh.write("\n\n"+repr(rule))

            fh.write("\n")

    def _parseAlias(self,line,marker):
        res = {}

        aliasRE = re.compile(r"\s*%s\s*(\S+)\s*=\s*((\S+,?\s*)+)" % marker)
        m = aliasRE.search(line)
        if(m):
            alias = str(m.group(1))
            nodes = str(m.group(2)).split(",")
            nodes = [ node.strip() for node in nodes ]
            res[alias] = sorted(nodes, key=lambda d: d.lower().replace("_", "~"))

        return res

    def _parseRule(self,line, commentLine):
        ruleRE = re.compile(r"\s*(\S+)\s*(\S+)\s*=\s*(.*)")
        ruleCommentRE = re.compile(r"^\s*#\s*NAME=(.*)")

        runasRE = re.compile(r"^\s*\((\S+)\)(.*)")
        m = ruleRE.search(line)
        n = ruleCommentRE.search(commentLine)
        if(m and n):
            user = str(m.group(1))
            host = str(m.group(2))
            cmd = str(m.group(3))
            r = runasRE.search(cmd)
            if r:
                command = SudoCmnd(r.group(1),r.group(2))
            else:
                command = SudoCmnd("", cmd)
            return SudoRule(user,host,command,n.group(1))

    def _collapseLines(self,lines):
        res = []
        currentline = ""

        for line in lines:
            if(line.rstrip()[-1:] == "\\"):
                currentline += line.rstrip()[:-1]
            else:
                currentline += line
                res.append(currentline)
                currentline = ""

        return res

def main():
    if len(sys.argv) != 2:
        print "Usage: sort_sudoers.py FILENAME"
        exit(1)
    sp = SudoersParser()
    err = sp.parseFile(sys.argv[1])
    if err != "":
        print err
        exit(1)
    sp.outputFile(sys.argv[1])

if(__name__ == "__main__"):
    main()
