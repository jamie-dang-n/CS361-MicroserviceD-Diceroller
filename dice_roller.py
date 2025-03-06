import zmq
import json
import random

"""
LISTENS ON PORT 5552
Expected input format: jsonified dictionary
input_dict {
    "option": [value is 0, 1, or 2] [REQUIRED]
    "n": an integer representing number of faces [REQUIRED]
    "operation": the operation to do (addition or subtraction) [OPTIONAL]
    "m": an integer to add/subtract [OPTIONAL]
}

option = 0: quit the microservice
option = 1: roll a dice with n faces
option = 2: roll a dice with n faces and do the given mathematical operation (in the form "[operator] m", where m is an integer and [operator] is + or - (addition or subtraction ONLY))
"""

# convertInt is used to convert fields
# from the input dictionary (hasValidData and option)
# to an integer. if conversion fails, the int = -1
def convertInt(dict, field):
    returnInt = 0
    try:
        if (dict[field]):
            returnInt = int(dict[field])
    except ValueError:
        returnInt = -1
    return returnInt

def main():
    # set up ZeroMQ
    context = zmq.Context()
    socket = context.socket(zmq.REP)

    # Binds REP socket to tcp://localhost:5552
    socket.bind("tcp://localhost:5552")
    proceed = 1 # continue waiting for next request while option != 0
    while (proceed != 0):
        print("Dice Rolling Service Listening...")
        request = socket.recv()
        print(f"Received request: {request}")

        # convert byte string message to json
        decoded = json.loads(request.decode('utf-8'))
        print(f"Decoded request: {decoded}")

        # check if option is 0-- if it is, quit the service
        proceed = convertInt(decoded, "option")
        if (proceed != 0):
            option = decoded['option']
            n = convertInt(decoded, "n")

            # roll a dice with n faces
            dice_roll = random.randint(1, n)
            
            if(option == 2):
                # roll a dice with n faces and use the operation (+ or -) with the modifier m
                m = convertInt(decoded, "m")
                if (decoded['operation'] == "+"):
                    dice_roll += m
                elif (decoded['operation'] == "-"):
                    dice_roll -= m

            # return the result
            byte_dice_roll = dice_roll.to_bytes(4, byteorder='big') # byte string is 4 bytes, in big-endian
            print(f"Response: {byte_dice_roll}")
            socket.send(byte_dice_roll)
        else:
            print("Dice rolling Microservice has ended.")
            socket.send_string("") # send back empty string

if __name__ == "__main__":
    main()