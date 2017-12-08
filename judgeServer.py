# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
app = Flask(__name__)


class Target:

    def __init__(self, name, id, point):
        self.id = id
        self.name = name
        self.player = "n"
        self.point = point

    def makeJson(self):
        json = {
            "name": self.name,
            "player": self.player,
            "point": self.point,
            # "id": self.id,
        }
        return json


class WarState:
    def __init__(self):
        self.state = "end"
        self.players = {"r": "NoPlayer", "b": "NoPlayer"}
        self.ready = {"r": False, "b": False}
        self.scores = {"r": 0, "b": 0}
        self.targets = []

    def makeJson(self):
        json = {
            "players": self.players,
            "ready": self.ready,
            "scores": self.scores,
            "state": self.state,
            "targets": [t.makeJson() for t in self.targets],
        }
        return json

class Response:
    def __init__(self):
        self.mutch = False
        self.new = False
        self.error = "yet init"
        self.target = None

    def makeJson(self):
        if self.target is None:
            target = None
        else:
            target = self.target.makeJson()
        json = {
            "mutch": self.mutch,
            "new": self.new,
            "error": self.error,
            "target": target
        }
        return json



class Referee:
    def __init__(self):
        self.war_state = WarState()

    def judgeTargetId(self, player_name, player_side, target_id):
        '''
        target_id must be string and length is "4"
        return "False" or "target json"
        '''
        # make Response object
        response = Response()
        # check id length
        if not len(target_id) == 4:
            print("ERROR target length is not 4")
            print("player_name: " + player_name)
            print("player_side: " + player_side)
            print("target_id: " + target_id)
            renponse.error = "ERR id length is not 4"
            return renponse.makeJson()
        # set ready if id = 0000
        if target_id == "0000":
            self.war_state.ready[player_side] = True
            response.mutch = True
            response.error = "success set ready"
            return response.makeJson()

        # check state is running
        if self.war_state.state != "running":
            response.error = "ERR state is not running"
            return response.makeJson()

        for target in self.war_state.targets:
            if target_id == target.id:
                is_new = self.updateWarState(target, player_name, player_side)
                response.mutch = True
                response.new = is_new
                response.error = "no error"
                response.target = target
                return response.makeJson()
        response.error = "ERR not mutch id"
        return response.makeJson()

    def checkBothPlayerReady(self):
        if self.war_state.ready["r"] and self.war_state.ready["b"]:
            self.war_state.state = "running"
        return

    def updateWarState(self, target, player_name, player_side):
        if not target.player == "n":
            return False
        else:
            target.player = player_side
            self.war_state.scores[player_side] += target.point
        return True

    def registPlayer(self, name):
        if self.war_state.players['r'] == "NoPlayer":
            self.war_state.players['r'] = name
            ret = {"side": "r", "name": name}
        elif self.war_state.players['b'] == "NoPlayer":
            self.war_state.players['b'] = name
            ret = {"side": "b", "name": name}
        else:
            ret = "##Errer 2 player already registed"
        return ret

    def registTarget(self, name, target_id, point):
        target = Target(name, target_id, point)
        self.war_state.targets.append(target)
        return target.name

    def setState(self, state):
        if state == "end":
            self.war_state.state = state
        elif state == "running":
            if self.checkBothPlayerReady():
                self.war_state.state = state
        elif state == "stop":
            self.war_state.state = state
        else:
            pass
        return state


# global object referee
referee = Referee()


@app.route('/')
def index():
    msg = "Hello, Welcome to ONIGIRI WAR!"
    return msg


@app.route('/submits', methods=['POST'])
def judgeTargetId():
    body = request.json
    player_name = body["name"]
    player_side = body["side"]
    target_id = body["id"]
    response = referee.judgeTargetId(player_name, player_side, target_id)
    return jsonify(response)


@app.route('/warState', methods=['GET'])
def getState():
    state_json = referee.war_state.makeJson()
    return jsonify(state_json)


@app.route('/warState/players', methods=['POST'])
def registPlayer():
    body = request.json
    name = body["name"]
    ret = referee.registPlayer(name)
    return jsonify(ret)


@app.route('/warState/targets', methods=['POST'])
def registTarget():
    body = request.json
    name = body["name"]
    target_id = body["id"]
    point = body["point"]
    ret = referee.registTarget(name, target_id, point)
    return jsonify({"name": ret})


@app.route('/warState/state', methods=['POST'])
def setState():
    body = request.json
    state = body["state"]
    ret = referee.setState(state)
    return jsonify({"state": ret})


@app.route('/reset', methods=['GET'])
def reset():
    global referee
    referee = Referee()
    return jsonify("reset")


@app.route('/test', methods=['GET'])
def getTest():
    return jsonify({
                     "foo": "bar",
                     "hoge": "hogehoge"
                   })


@app.route('/test', methods=['POST'])
def postTest():
    ret = request.json
    return jsonify(ret)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
