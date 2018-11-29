import requests, json
from collections import defaultdict

headers = {'content-type': 'application/x-www-form-urlencoded'}
token = ''

#Constants
DONE = 0
HIT_WALL = 1
VISITED = 2
EXPIRED = 3
GAME_OVER = 4
NO_SOL = 5

def getNewToken():
    global token
    data = {'uid': '504992961'}
    r = requests.post('http://ec2-34-216-8-43.us-west-2.compute.amazonaws.com/session', data=data, headers=headers)
    checkError(r.status_code)
    token = json.loads(r.text)['token']

def checkError(x):
    if x != requests.codes.ok:
        print "Error " + x + ": bad request"
        quit()

def isInBounds(currx, curry, sizex, sizey):
    if currx < 0 or currx >= sizex or curry < 0 or curry >= sizey:
        return False
    else:
        return True

#result: WALL, SUCCESS, OUT_OF_BOUNDS, END, or EXPIRED
def solve(d, size, result):
    global token
    #print "-------------------"
    #print("Status:"+result)
    if result == "END":
        print 'Level complete'
        return DONE
    if result == "WALL":
        return HIT_WALL
    if result == "EXPIRED":
        print 'Session expired'
        return EXPIRED

    #get request
    url = 'http://ec2-34-216-8-43.us-west-2.compute.amazonaws.com/game?token='+token
    g = requests.get(url, headers=headers)
    checkError(g.status_code)
    body = json.loads(g.text)
    state = body['status']
    curr = body['current_location']

    if state == "NONE":
        print 'Session expired'
        return EXPIRED
    if state == "GAME_OVER":
        print 'Game over: game ended prematurely'
        return GAME_OVER
    
    x = curr[0]
    y = curr[1]
    #print('Current loc: '+str(x)+' '+str(y))

    if d[(x,y)] == 1:    #check if spot is visited
        return VISITED
    d[(x,y)] = 1    #mark spot as visited

    if result == "SUCCESS": #moved successfully
        if isInBounds(x, y-1, size[0], size[1]):    #UP
            p = requests.post(url, data={'action': 'UP'}, headers=headers)
            checkError(p.status_code)
            result = json.loads(p.text)['result']
            stat = solve(d, size, result)
            if stat == DONE:
                return DONE
            elif stat == EXPIRED or stat == GAME_OVER:
                return stat
            elif stat != HIT_WALL:   #no solution this way; go back ONLY IF NO WALL
                p = requests.post(url, data={'action': 'DOWN'}, headers=headers)
                checkError(p.status_code)

        if isInBounds(x, y+1, size[0], size[1]):    #DOWN
            p = requests.post(url, data={'action': 'DOWN'}, headers=headers)
            checkError(p.status_code)
            result = json.loads(p.text)['result']
            stat = solve(d, size, result)
            if stat == DONE:
                return DONE
            elif stat == EXPIRED or stat == GAME_OVER:
                return stat
            elif stat != HIT_WALL:
                p = requests.post(url, data={'action': 'UP'}, headers=headers)
                checkError(p.status_code)

        if isInBounds(x-1, y, size[0], size[1]):    #LEFT
            p = requests.post(url, data={'action': 'LEFT'}, headers=headers)
            checkError(p.status_code)
            result = json.loads(p.text)['result']
            stat = solve(d, size, result)
            if stat == DONE:
                return DONE
            elif stat == EXPIRED or stat == GAME_OVER:
                return stat
            elif stat != HIT_WALL:
                p = requests.post(url, data={'action': 'RIGHT'}, headers=headers)
                checkError(p.status_code)

        if isInBounds(x+1, y, size[0], size[1]):    #RIGHT
            p = requests.post(url, data={'action': 'RIGHT'}, headers=headers)
            checkError(p.status_code)
            result = json.loads(p.text)['result']
            stat = solve(d, size, result)
            if stat == DONE:
                return DONE
            elif stat == EXPIRED or stat == GAME_OVER:
                return stat
            elif stat != HIT_WALL:
                p = requests.post(url, data={'action': 'LEFT'}, headers=headers)
                checkError(p.status_code)
            
    return NO_SOL   #should never reach this


def main():
    global token
    token_expired = False
    stop = False
    
    while True:
        getNewToken()
        g = requests.get('http://ec2-34-216-8-43.us-west-2.compute.amazonaws.com/game?token='+token, headers=headers)
        checkError(g.status_code)
        print g.text
        body = json.loads(g.text)
        size = body['maze_size']                #[width, height]
        curr = body['current_location']         #[xcol, ycol]
        state = body['status']                  #PLAYING, GAME_OVER, NONE, FINISHED
        levels_completed = body['levels_completed']
        total = body['total_levels']
        
        d = defaultdict(int)
        
        while levels_completed < total:
            stat = solve(d, size, 'SUCCESS')    #solve the current level
            if stat == EXPIRED:
                token_expired = True
                break
            elif stat != DONE:  #if GAME_OVER
                stop = True
                break
            g = requests.get('http://ec2-34-216-8-43.us-west-2.compute.amazonaws.com/game?token='+token, headers=headers)
            checkError(g.status_code)
            print g.text
            d2 = defaultdict(int)
            d = d2
            body = json.loads(g.text)
            size = body['maze_size']                #[width, height]
            curr = body['current_location']         #[xcol, ycol]
            state = body['status']                  #PLAYING, GAME_OVER, NONE, FINISHED
            levels_completed = body['levels_completed']
            total = body['total_levels']
            if state == "FINISHED":
                stop = True
                print 'All levels complete'
                break
            elif state != "PLAYING":
                stop = True
                print('Error: game ended prematurely with state '+state)
                break
        if token_expired:
            continue
        if stop:
            break
    print "End program"


if __name__ == "__main__":
    main()
