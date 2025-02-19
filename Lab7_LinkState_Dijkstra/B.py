from collections import defaultdict
import heapq as heap
import math
import os
import socket
import threading
import time
import random
from concurrent.futures import ThreadPoolExecutor

curr='B'
ipport={"A":(9771),"B":(9772),"C":(9773),"D":(9774),"E":(9775),"F":(9776)}
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
G = {}
neighbour=[]
def update_graph():
	while True:
		time.sleep(30)
		id=curr+' 60\n'
		s=''
		node=chr(random.randrange(65, 65 + 4))
		cost=random.randint(1,50)
		if node==curr:
			continue
		G[curr][node]=cost
		G[node][curr]=cost
		print(f"Updating cost {curr} {node} {cost}")
		s+=curr+' '+str(node)+' '+str(cost)+'@'
		if s!='':
			msg=id+s
			msg_to_neighbour(msg)
			parentsmap,nodecost=dijkstra(G,curr)
			print_cost(nodecost,parentsmap)





def dijkstra(G, startingNode):
	visited = set()
	parentsMap = {}
	pq = []
	nodeCosts = defaultdict(lambda:math.inf)
	nodeCosts[startingNode] = 0
	heap.heappush(pq, (0, startingNode))
 
	while pq:
		# go greedily by always extending the shorter cost nodes first
		_, node = heap.heappop(pq)
		visited.add(node)
 
		for adjNode, weight in G[node].items():
			if adjNode in visited:	continue
				
			newCost = nodeCosts[node] + int(weight)
			if nodeCosts[adjNode] > newCost:
				parentsMap[adjNode] = node
				nodeCosts[adjNode] = newCost
				heap.heappush(pq, (newCost, adjNode))
        
	return parentsMap, nodeCosts
def initial_strt():
	
	with open('init.txt', 'r') as file:
		for line in file:
			src,dest,cost=line.split()
		
			if src==curr:
				if src not in G:
					G[src]={}
				if dest not in G:
					G[dest]={}
				G[src][dest]=cost
				G[dest][src]=cost
				neighbour.append(dest)
	
	# G = {
	# 	curr: {curr: 2, 'D': 1},
	# 	curr: {curr: 2, 'D': 7,'C': 4},
	# 	'C': {curr: 4},
	# 	'D': {curr: 1,curr:7},
	
	# }
	print(G)
	parentsMap, nodeCosts=dijkstra(G,startingNode=curr)
	print_cost(nodeCosts,parentsMap)
	


	
def handle_client(conn, addr):
	data = conn.recv(1024).decode()
	msg_parse(data)

def print_shortest_paths(parentsMap, sourceNode):
    print("Path:\n")
    for destNode in parentsMap:
        path = []
        node = destNode
        while node != sourceNode:
            if node not in parentsMap:
                print(f"No path from {sourceNode} to {destNode}")
                break
            path.append(node)
            node = parentsMap[node]
        else:
            path.append(sourceNode)
            print(f"Shortest path from {sourceNode} to {destNode}: {' -> '.join(reversed(path))}")

def print_cost(nodecost,parentmap):
	print(f'\nNew Table for {curr}:\n')
	for i in nodecost:
		print(f"{i} {nodecost.get(i)}")
	print('')
	print_shortest_paths(parentmap,curr)
def msg_to_neighbour(msg):
	for nei in neighbour:
		n_ip=''
		n_port=ipport[nei]
		cl=socket.socket()
		try:
			cl.connect((n_ip,n_port))
			cl.send(msg.encode())
		except:
			print(f"{curr} couldn't connect with neigbour {nei} on port {n_port}")
		cl.close()
def msg_parse(msg):
	tmp=msg
	msg=msg.split('\n')
	id,ttl=msg[0].split()
	if id==curr:
		return
	else:
		msg_to_neighbour(tmp)
		dat=msg[1].split('@')
		for line in dat:
			try:
				src,dest,weight=line.split()
			except:
				break
			if src not in G:
				G[src]={}
			if dest not in G:
				G[dest]={}
			G[src][dest]=weight
			G[dest][src]=weight
		print('\nG updated\n')
		#print(G)
		parentsmap,nodecost=dijkstra(G,curr)
		print_cost(nodecost,parentsmap)

	
def msg_send():
    
	id=curr+' 60\n'
	s=''
	for adjNode, weight in G[curr].items():
		s+=curr+' '+str(adjNode)+' '+str(weight)+'@'
	msg=id+s
	msg_to_neighbour(msg)
    
        
def main():
    a = input()

    initial_strt()
    print("[STARTING] Server is starting")
    sock = socket.socket()
    sock.bind(('', 9772))
    sock.listen()
    IP = ''
    PORT = 9772
    print(f"[LISTENING] sock is listening on {IP}:{PORT}.")
    time.sleep(10)
    initial_msg_thread = threading.Thread(target=msg_send)
    initial_msg_thread.start()
    update_thread = threading.Thread(target=update_graph)
    update_thread.start()

    # Define a thread pool with a maximum of, for example, 10 threads
    with ThreadPoolExecutor(max_workers=10) as executor:
        while True:
            conn, addr = sock.accept()
            # Submit the connection handling to the thread pool
            executor.submit(handle_client, conn, addr)

main()
