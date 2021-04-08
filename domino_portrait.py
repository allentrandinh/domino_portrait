from PIL import Image as im
import numpy as np
import random
import itertools
import gurobipy as gp
from gurobipy import GRB

def pic_to_array(pic_path,dom_num):
    #receives photo of ratio 10x11 (heightxwidth)
    image = im.open(pic_path)
    data = np.asarray(image)
    height = data.shape[0]
    width = data.shape[1]
    rescale_factor = int(height/(10*dom_num))

    def index_gen(num1,num2,num3):
        '''
        :param num1: row number
        :param num2: col number
        :param num3: width/height of square to be covered from (num1,num2) element
        :return:
        '''
        num1_bound = num1+num3
        num2_bound = num2+num3
        indices = []
        for index in range(num1,num1_bound):
            for index2 in range(num2,num2_bound):
                indices.append((index,index2))
        return indices

    def square_average(mat,indices,num3):
        total = 0
        for i in indices:
            total += mat[i]
        return(int(total/(num3**2)))

    def standard(image_array,h,w,factor):
        new_array = np.empty(110*(dom_num**2))
        i=0
        for row in range(0,h,factor):
            for column in range(0,w,factor):
                new_array[i] = square_average(image_array,index_gen(row,column,factor),factor)
                i += 1
        return(np.reshape(new_array,(10*dom_num,11*dom_num)))

    dom_array = standard(data,height,width,rescale_factor)
    im.fromarray(dom_array).show()
    dom_array = np.rint(dom_array/255*9)
    np.savetxt('./file/dom_array_txt',dom_array,delimiter='\t')
    np.save('./file/dom_array',dom_array)

def neighbor_find(mat,a,b):
    '''
    :return: list of empty neighbor
    '''
    empt = []
    if b<mat.shape[1]-1 and mat[a,b+1]==0:
        empt.append((a,b+1))
    if a<mat.shape[0]-1 and mat[a+1,b]==0:
        empt.append((a+1,b))
    return empt

def search_other_half(matt,a,b):
    '''
    :return: return location of the other half of the domino
    '''
    value = matt[a,b]
    indices=((a,b+1),(a,b-1),(a-1,b),(a+1,b))
    for index in indices:
        if index[1]<=matt.shape[1]-1 and index[0]<=matt.shape[0]-1:
            if matt[index] == value:
                return(index)

def find_first_empty(matt):
    total_row = matt.shape[0]
    total_column = matt.shape[1]
    for i in range (0,total_row):
        for m in range(0,total_column):
            if matt[i,m]==0:
                return((i,m))

def pattern_generator(arr,start,piece_num):
    #generate pattern in small area of size 10xdom_num
    numbering = []
    row = arr.shape[0]
    col = arr.shape[1]
    for i in range(start,start+piece_num):
        numbering.append(i)

    while len(numbering)>0:
        curr = numbering[0]
        #location of first empty cell
        x,y = find_first_empty(arr)
        list_neighbor = neighbor_find(arr,x,y)
        if len(list_neighbor)==0:
            coord = [(x-2,x-1,x,x+1,x+2),(y-2,y-1,y,y+1,y+2)]
            index_to_be_del = list(itertools.product(*coord))
            for ind in index_to_be_del:
                if 0<=ind[0]<row and 0<=ind[1]<col:
                    if arr[ind]!=0:
                        numbering.append(int(arr[ind]))
                        other_half = search_other_half(arr,ind[0],ind[1])
                        arr[ind] =0
                        arr[other_half]=0
        elif len(list_neighbor)==1:
            arr[x,y] = curr
            arr[list_neighbor[0]]=curr
            numbering.remove(curr)
        elif len(list_neighbor)==2:
            arr[x, y] = curr
            choice = random.randint(0,1)
            arr[list_neighbor[choice]]=curr
            numbering.remove(curr)

def domino_piece_generator():
    pieces = []
    for a in range (0,10):
        for b in range (a,10):
            pieces.append((a,b))
    return(pieces)

def location_generator(a,b):
    '''
    :param a: number of rows
    :param b: number of columns
    :return: list of coordinates
    '''
    coord = [[],[]]
    for i in range (0,a):
        coord[0].append(i)
    for k in range (0,b):
        coord[1].append(k)
    loc = itertools.product(*coord)
    return list(loc)

def area_dictionary_generator(domino_pieces):
    '''create a dictionary with domino piece as key to store their corresponding amounts in portrait array'''
    area = {}
    for piece in domino_pieces:
        area[piece] = 0
    return area

def correct_order(value1,value2):
    '''return 2 values in a domino with increasing order'''
    if value2 < value1:
        return (value2,value1)
    else:
        return (value1,value2)

def print_dictionary(di):
    for key in di.keys():
        print(key, di[key])

def calculate_cost(area,domino):
    '''
    :param area: 2 values of each area
    :param domino: 2 values for the domino
    :return: smallest cost between 2 orientations
    '''
    cost_1 = (area[0]-domino[0])**2 + (area[1]-domino[1])**2
    cost_2 = (area[0]-domino[1])**2 + (area[1]-domino[0])**2
    return int(min(cost_1,cost_2))

def matrix_gen(area_list,dominoes_list):
    col = len(area_list)
    row = len(dominoes_list)
    cost_matrix = np.zeros((row, col))
    for r in range (0,row):
        for c in range (0,col):
            cost_matrix[r,c] = calculate_cost(dominoes_list[r],area_list[c])
    return cost_matrix

def obtain_piece(dom_dictionary,key):
    temp = dom_dictionary[key][0]
    del dom_dictionary[key][0]
    return temp

def swap_or_not(dom,first_val_loc,second_val_loc,piece):
    cost_1 = (dom[first_val_loc]-piece[0])**2 + (dom[second_val_loc]-piece[1])**2
    cost_2 = (dom[first_val_loc]-piece[1])**2 + (dom[second_val_loc]-piece[0])**2
    if cost_1<cost_2:
        return False
    else:
        return True

def full_pattern_generator(dom_num,small_square_size,num_random_pattern):
    '''
    :param dom_num: number of domino to be used in the canvas
    :param small_square_size: small area of pattern to be generated, not exceeding 50, needs to be even
    :return:
    '''
    # pattern_generator: only needs to be ran once, can be reused
    # create domino orientation for the entire canvas
    # generate 9 different patterns for 10x5 squares
    num_pat_needed = int(((dom_num**2)*110)/(small_square_size[0]*small_square_size[1]))
    piece_num_needed = int(small_square_size[0]*small_square_size[1]/2)
    patterns = []
    for i in range(0, num_random_pattern):
        arr = np.zeros((small_square_size[0], small_square_size[1]))
        pattern_generator(arr, 1 + piece_num_needed * i,piece_num_needed)
        patterns.append(arr)
        #print("Pattern " + str(i) + "generated")

    horizontal_num = int(11*dom_num/small_square_size[1])
    vertical_num = int(10*dom_num/small_square_size[0])
    new_array = []
    for i in range(0,vertical_num):
        temp = []
        for k in range(0,horizontal_num):
            temp.append(patterns[random.randint(0,num_random_pattern-1)])
        new_array.append(np.hstack(temp[:]))
    final = np.vstack(new_array[:])

    np.save("./file/final_pattern", final)

    print("Pattern Successfully saved")

    '''
    #in case want to save each pattern
    for i in range(0, 11):
        name = "./file/pattern_" + str(i + 1)
        np.save(name, patterns[i])
    
    '''

def portrait_gen(dom_num,dom_size):
    #portrait array and domino pattern load
    dom = np.load('./file/dom_array.npy')
    pattern = np.load('./file/final_pattern.npy')
    print(dom.shape)
    print(pattern.shape)
    print(dom_num*10, dom_num*11)

    def update_area_count(areas, pattern):
        loc = location_generator(dom_num*10, dom_num*11)
        for location in loc:
            if pattern[location] != 0:
                # current location looking at: location
                # search other half of the domino
                other_half = search_other_half(pattern, location[0], location[1])
                value_pair = correct_order(dom[location], dom[other_half])
                # add total of that area in the dictionary by 1
                areas[value_pair] = areas[value_pair] + 1
                # change number of corresponding pattern into 0
                pattern[location], pattern[other_half] = 0, 0
        updated_area = {}
        for key in areas.keys():
            if areas[key] != 0:
                updated_area[key] = areas[key]
        return updated_area

    #generate domino pieces and location
    pieces = domino_piece_generator()
    loc = location_generator(dom_num*10, dom_num*11)

    #create a dictionary with domino piece as key to store their corresponding amounts in portrait array
    areas = area_dictionary_generator(pieces)

    #update area dictionary to correct count of each area
    areas = update_area_count(areas,pattern)

    #generate list of area and list of dominoes
    area = list(areas.keys())
    dominoes = domino_piece_generator()

    #generate cost matrix
    cost_matrix = matrix_gen(area,dominoes)
    np.savetxt('./file/cost_matrix',cost_matrix,delimiter='\t')
    np.save('./file/np_cost_matrix',cost_matrix)

    #get list of capacities for each area
    capa = list(areas.values())
    area_num = len(area)
    domino_set_num = dom_num**2

#    cost_matrix = np.load('./np_cost_matrix.npy')

    try:
        # create a new model
        m = gp.Model('domino_portrait')

        # create variables
        x = m.addMVar(shape=(55, area_num), vtype=GRB.INTEGER, name="x")

        # set objective
        # sum up each row then sum them up together
        m.setObjective(sum(cost_matrix[j, :] @ x[j, :] for j in range(0, 55)), GRB.MINIMIZE)

        # set parameters to ensure integrality
        m.setParam('MIPFocus', 3)
        m.setParam('IntegralityFocus', 1)
        m.setParam('IntFeasTol', 1e-9)

        # set constraints:
        # m.addMConstr(matrix55, x,'=',rhs_area_capacity_constraint,name = "domino_num_constr")
        for r in range(0, 55):
            m.addConstr(sum(x[r, j] for j in range(0, area_num)) == domino_set_num)
        for c in range(0, area_num):
            m.addConstr(sum(x[i, c] for i in range(0, 55)) == capa[c])
        # m.addMConstr(matrix55_1D,np.transpose(x),'=',rhs_domino_type_constraint,name="domino_num_constr")
        # m.addMConstr(matrix_capa_1D,x,'=',rhs_area_capacity_constraint,name="domino_num_constr")
        # m.addConstr(np.sum(x,axis=1) == rhs_domino_type_constraint,name="domino_num_constr")
        # m.addConstr(sum(x[:,j] for j in range (0,area_num)) == rhs_area_capacity_constraint,name="domino_num_constr")

        # m.addMConstr(matrixcapa, x,'=', rhs_area_capacity_constraint,name="capa_constr")

        # optimize the model:
        m.optimize()
        np.save('./file/domino_assignment_sol', x.X)
        np.savetxt('./file/domino_assignment_sol', x.X, delimiter='\t')

    except gp.GurobiError as e:
        print('Error code ' + str(e.errno) + ": " + str(e))

    except AttributeError:
        print('Encountered an attribute error')

    sol = np.rint(np.load('./file/domino_assignment_sol.npy'))

    # construct dictionary with area as key and empty list

    area_piece = {}
    for item in area:
        area_piece[item] = []

    # add corresponding amount of domino of each type to each area
    for c in range(0, len(area)):
        for r in range(0, 55):
            for count in range(0, int(sol[r, c])):
                area_piece[area[c]].append(dominoes[r])

    # shuffle all the domino within an area
    for ar in area:
        random.shuffle(area_piece[ar])

    canvas = im.new(mode="RGB", size=(11 *dom_num * dom_size, 10*dom_num*dom_size), color=(0, 0, 0))
    print("\n")
    print("Your canvas size is: " + str(11 *dom_num * dom_size) +", " +str(10 *dom_num * dom_size))

    pattern = np.load('./file/final_pattern.npy')
    for location in loc:
        if pattern[location] != 0:
            image_coord = (location[1] * dom_size, location[0] * dom_size)
            # current location looking at: location
            # search other half of the domino
            other_half = search_other_half(pattern, location[0], location[1])

            # obtain corresponding domino piece from dictionary
            area_pair = correct_order(dom[location], dom[other_half])
            cur_piece = obtain_piece(area_piece, area_pair)
            piece_name = "./domino_generator/" + str(cur_piece[0]) + str(cur_piece[1]) + ".png"
            open_image = im.open(piece_name)

            # current domino orientation is vertical, rotate image by 90 degree
            if other_half[1] > location[1]:
                open_image = open_image.transpose(im.ROTATE_90)

            if swap_or_not(dom, location, other_half, cur_piece) is True:
                open_image = open_image.transpose(im.FLIP_TOP_BOTTOM).transpose(im.FLIP_LEFT_RIGHT)

            canvas.paste(open_image, image_coord)

            # change number of corresponding pattern into 0
            pattern[location], pattern[other_half] = 0, 0

    canvas.show()
    canvas.save("./domino_portrait_result/portrait_generated.png")


#supply path to picture, assume at right size and grayscale

pic_to_array('./image/264x240_mona.jpg',12)

#para1: amount of domino to be used
#para2: list of rowxheight small square where pattern is to be generated, not to exceed 50
#recommend for para2 = [para1/2, para1/2]
#para: number of random pattern of size (para2) to be generated

full_pattern_generator(12,[6,6],15)

portrait_gen(12,42)










