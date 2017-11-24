import angr
p=angr.Project('use_your_ida.exe',load_options={"auto_load_libs":False})
find=(0x401077,)
avoid=(0x401083,0x42f91a)
main=0x413142
init=p.factory.blank_state(addr=main)
for i in range(24):
	a=init.se.BVS('a',8)
	init.se.add(a>32)
	init.se.add(a<127)
	init.mem[init.regs.esp-28+i:].char=a
	init.mem[0x43f322+i:].char=a
simgr=p.factory.simulation_manager(init)
result=simgr.explore(find=find,avoid=avoid)
print(result)
s=result.found[0].state
flag=s.se.any_str(s.memory.load(0x43f322,100))
print flag
