import math


class Reward:
    def __init__(self, verbose=False):
        self.first_racingpoint_index = None
        self.verbose = verbose

    def reward_function(self, params):

        # Import package (needed for heading)
        # import math

        ################## HELPER FUNCTIONS ###################

        def dist_2_points(x1, x2, y1, y2):
            return abs(abs(x1-x2)**2 + abs(y1-y2)**2)**0.5

        def closest_2_racing_points_index(racing_coords, car_coords):

            # Calculate all distances to racing points
            distances = []
            for i in range(len(racing_coords)):
                distance = dist_2_points(x1=racing_coords[i][0], x2=car_coords[0],
                                         y1=racing_coords[i][1], y2=car_coords[1])
                distances.append(distance)

            # Get index of the closest racing point
            closest_index = distances.index(min(distances))

            # Get index of the second closest racing point
            distances_no_closest = distances.copy()
            distances_no_closest[closest_index] = 999
            second_closest_index = distances_no_closest.index(
                min(distances_no_closest))

            return [closest_index, second_closest_index]

        def dist_to_racing_line(closest_coords, second_closest_coords, car_coords):
            
            # Calculate the distances between 2 closest racing points
            a = abs(dist_2_points(x1=closest_coords[0],
                                  x2=second_closest_coords[0],
                                  y1=closest_coords[1],
                                  y2=second_closest_coords[1]))

            # Distances between car and closest and second closest racing point
            b = abs(dist_2_points(x1=car_coords[0],
                                  x2=closest_coords[0],
                                  y1=car_coords[1],
                                  y2=closest_coords[1]))
            c = abs(dist_2_points(x1=car_coords[0],
                                  x2=second_closest_coords[0],
                                  y1=car_coords[1],
                                  y2=second_closest_coords[1]))

            # Calculate distance between car and racing line (goes through 2 closest racing points)
            # try-except in case a=0 (rare bug in DeepRacer)
            try:
                distance = abs(-(a**4) + 2*(a**2)*(b**2) + 2*(a**2)*(c**2) -
                               (b**4) + 2*(b**2)*(c**2) - (c**4))**0.5 / (2*a)
            except:
                distance = b

            return distance

        # Calculate which one of the closest racing points is the next one and which one the previous one
        def next_prev_racing_point(closest_coords, second_closest_coords, car_coords, heading):

            # Virtually set the car more into the heading direction
            heading_vector = [math.cos(math.radians(
                heading)), math.sin(math.radians(heading))]
            new_car_coords = [car_coords[0]+heading_vector[0],
                              car_coords[1]+heading_vector[1]]

            # Calculate distance from new car coords to 2 closest racing points
            distance_closest_coords_new = dist_2_points(x1=new_car_coords[0],
                                                        x2=closest_coords[0],
                                                        y1=new_car_coords[1],
                                                        y2=closest_coords[1])
            distance_second_closest_coords_new = dist_2_points(x1=new_car_coords[0],
                                                               x2=second_closest_coords[0],
                                                               y1=new_car_coords[1],
                                                               y2=second_closest_coords[1])

            if distance_closest_coords_new <= distance_second_closest_coords_new:
                next_point_coords = closest_coords
                prev_point_coords = second_closest_coords
            else:
                next_point_coords = second_closest_coords
                prev_point_coords = closest_coords

            return [next_point_coords, prev_point_coords]

        def racing_direction_diff(closest_coords, second_closest_coords, car_coords, heading):

            # Calculate the direction of the center line based on the closest waypoints
            next_point, prev_point = next_prev_racing_point(closest_coords,
                                                            second_closest_coords,
                                                            car_coords,
                                                            heading)

            # Calculate the direction in radius, arctan2(dy, dx), the result is (-pi, pi) in radians
            track_direction = math.atan2(
                next_point[1] - prev_point[1], next_point[0] - prev_point[0])

            # Convert to degree
            track_direction = math.degrees(track_direction)

            # Calculate the difference between the track direction and the heading direction of the car
            direction_diff = abs(track_direction - heading)
            if direction_diff > 180:
                direction_diff = 360 - direction_diff

            return direction_diff

        # Gives back indexes that lie between start and end index of a cyclical list 
        # (start index is included, end index is not)
        def indexes_cyclical(start, end, array_len):

            if end < start:
                end += array_len

            return [index % array_len for index in range(start, end)]

        # Calculate how long car would take for entire lap, if it continued like it did until now
        def projected_time(first_index, closest_index, step_count, times_list):

            # Calculate how much time has passed since start
            current_actual_time = (step_count-1) / 15

            # Calculate which indexes were already passed
            indexes_traveled = indexes_cyclical(first_index, closest_index, len(times_list))

            # Calculate how much time should have passed if car would have followed optimals
            current_expected_time = sum([times_list[i] for i in indexes_traveled])

            # Calculate how long one entire lap takes if car follows optimals
            total_expected_time = sum(times_list)

            # Calculate how long car would take for entire lap, if it continued like it did until now
            try:
                projected_time = (current_actual_time/current_expected_time) * total_expected_time
            except:
                projected_time = 9999

            return projected_time

        #################### RACING LINE ######################

        # Optimal racing line for the Spain track
        # Each row: [x,y,speed,timeFromPreviousPoint]
        racing_track = [[0.30866329, 2.83066357, 2.58784677],
                       [0.32365686, 2.68032849, 2.71755098],
                       [0.34542764, 2.53081654, 2.81341253],
                       [0.37330426, 2.38232769, 2.72441791],
                       [0.40683891, 2.23500252, 2.34600193],
                       [0.44635081, 2.08916823, 2.08421502],
                       [0.49380025, 1.94577739, 1.89327623],
                       [0.55110252, 1.80606322, 1.58779662],
                       [0.61999089, 1.67165703, 1.40402933],
                       [0.70430916, 1.54669471, 1.31976058],
                       [0.80593841, 1.4368022 , 1.30056822],
                       [0.92385573, 1.34663488, 1.33423729],
                       [1.05500604, 1.27880773, 1.41999453],
                       [1.19558315, 1.23362694, 1.56339385],
                       [1.34197643, 1.20943044, 1.78986547],
                       [1.49126653, 1.20319999, 2.16375192],
                       [1.64138417, 1.21101694, 2.85537346],
                       [1.79120521, 1.22854394, 3.33      ],
                       [1.94048601, 1.25164664, 3.33      ],
                       [2.08953357, 1.27651089, 3.33      ],
                       [2.23866951, 1.3008531 , 2.05635759],
                       [2.38822966, 1.32162214, 1.62156576],
                       [2.53853599, 1.33163728, 1.45097226],
                       [2.68830809, 1.32444111, 1.40025524],
                       [2.83452981, 1.29627569, 1.41738625],
                       [2.97407662, 1.24657405, 1.49613307],
                       [3.10468668, 1.17692122, 1.60371836],
                       [3.22534962, 1.09028546, 1.70513151],
                       [3.33582995, 0.98964971, 1.79048087],
                       [3.43600547, 0.87740791, 1.81299139],
                       [3.52556841, 0.75570315, 1.76859363],
                       [3.62573863, 0.64296552, 1.74774673],
                       [3.73606149, 0.54063004, 1.73190884],
                       [3.85572567, 0.44980635, 1.72797781],
                       [3.98376665, 0.3714944 , 1.74041933],
                       [4.11900573, 0.30646572, 1.75762033],
                       [4.25991363, 0.25519387, 1.76791051],
                       [4.40011423, 0.21888954, 1.77903533],
                       [4.48853354, 0.20296718, 1.7847725 ],
                       [4.58832633, 0.19114337, 1.73994838],
                       [4.71359242, 0.18526421, 1.72726302],
                       [4.85689784, 0.1912954 , 1.74782857],
                       [5.00442016, 0.21212338, 1.81054591],
                       [5.15019856, 0.24753797, 1.90050797],
                       [5.29232781, 0.29623349, 2.03300358],
                       [5.43011173, 0.35668947, 2.17176   ],
                       [5.56337751, 0.42717078, 2.3512919 ],
                       [5.69206977, 0.50617301, 2.55668681],
                       [5.81631628, 0.59214418, 2.76257049],
                       [5.93645685, 0.68377889, 2.94093379],
                       [6.05287109, 0.78010583, 3.15307761],
                       [6.16584682, 0.88044928, 3.33      ],
                       [6.27571797, 0.98418704, 3.33      ],
                       [6.3828299 , 1.09077317, 3.33      ],
                       [6.48725903, 1.19998978, 3.33      ],
                       [6.58904453, 1.31167383, 3.33      ],
                       [6.6882196 , 1.42568217, 3.33      ],
                       [6.78482218, 1.54187766, 3.33      ],
                       [6.87891093, 1.66011787, 3.33      ],
                       [6.97055191, 1.78026502, 3.33      ],
                       [7.05983155, 1.90217822, 3.33      ],
                       [7.14684913, 2.02571713, 3.33      ],
                       [7.23169231, 2.15075952, 3.33      ],
                       [7.31445217, 2.277192  , 3.33      ],
                       [7.39507329, 2.40499657, 3.33      ],
                       [7.47349988, 2.53416006, 3.33      ],
                       [7.54965382, 2.66467546, 3.33      ],
                       [7.62346988, 2.79652739, 3.33      ],
                       [7.69487002, 2.92970319, 3.33      ],
                       [7.76377031, 3.06418793, 3.33      ],
                       [7.83010391, 3.19995672, 3.33      ],
                       [7.89381108, 3.33697829, 3.33      ],
                       [7.95482087, 3.47522259, 3.33      ],
                       [8.0130477 , 3.61466193, 3.33      ],
                       [8.06836382, 3.75528204, 3.33      ],
                       [8.12030503, 3.89718084, 3.16619805],
                       [8.16838949, 4.0404315 , 3.01528836],
                       [8.2121268 , 4.18506517, 2.87315826],
                       [8.25102599, 4.33107408, 2.74887074],
                       [8.28454709, 4.47841144, 2.62520962],
                       [8.31214118, 4.62697244, 2.27246658],
                       [8.33318546, 4.77659508, 2.01817102],
                       [8.34542817, 4.92717764, 1.66000102],
                       [8.34645772, 5.07824206, 1.46706423],
                       [8.33096231, 5.22823324, 1.37183643],
                       [8.29489952, 5.37372669, 1.34470896],
                       [8.23665964, 5.51067574, 1.36403407],
                       [8.15711213, 5.63567059, 1.41602171],
                       [8.0586699 , 5.74646104, 1.50012876],
                       [7.94443893, 5.84186919, 1.61620021],
                       [7.81786495, 5.92173961, 1.74647329],
                       [7.68230225, 5.98685816, 1.90919572],
                       [7.54051121, 6.03843176, 2.1118736 ],
                       [7.39475718, 6.07812331, 2.32243012],
                       [7.24661977, 6.10784586, 2.51325424],
                       [7.09704256, 6.12921405, 2.72168386],
                       [6.94660902, 6.14339352, 2.7953021 ],
                       [6.79572312, 6.15141627, 2.85234014],
                       [6.64464341, 6.15359   , 2.76347904],
                       [6.4935813 , 6.15014315, 2.68646787],
                       [6.34278778, 6.14071471, 2.62903098],
                       [6.19257814, 6.12498012, 2.57575537],
                       [6.04326402, 6.10269886, 2.53278945],
                       [5.89512529, 6.07363843, 2.47792794],
                       [5.74846711, 6.03761536, 2.28877826],
                       [5.60369849, 5.99439311, 2.03576846],
                       [5.46171286, 5.9429018 , 1.86458609],
                       [5.32412349, 5.88131946, 1.75822782],
                       [5.19271227, 5.80822631, 1.69964648],
                       [5.06916145, 5.72278713, 1.69427334],
                       [4.9550809 , 5.62487859, 1.72453908],
                       [4.85182674, 5.51549115, 1.79840405],
                       [4.76015102, 5.39619106, 1.93154953],
                       [4.67993469, 5.26880151, 2.20658658],
                       [4.61022127, 5.13525258, 2.67089583],
                       [4.54885766, 4.99750418, 3.33      ],
                       [4.49332703, 4.85713914, 3.33      ],
                       [4.4415921 , 4.71521664, 1.91826627],
                       [4.38752952, 4.57433953, 1.5265662 ],
                       [4.32247907, 4.43910787, 1.39828871],
                       [4.24142989, 4.31453293, 1.39189468],
                       [4.14333271, 4.20459426, 1.44715417],
                       [4.0299996 , 4.11105889, 1.56334692],
                       [3.90415461, 4.03406657, 1.72553325],
                       [3.76882441, 3.97239586, 1.90647031],
                       [3.62680062, 3.92421197, 2.08209791],
                       [3.48039091, 3.88773692, 1.90956015],
                       [3.33144218, 3.86150121, 1.69551974],
                       [3.18114401, 3.84773496, 1.63619925],
                       [3.03067951, 3.84979773, 1.68049241],
                       [2.88202787, 3.86864441, 1.8546027 ],
                       [2.73645711, 3.90308925, 2.24797987],
                       [2.59425121, 3.95014237, 3.07976614],
                       [2.45472695, 4.0057079 , 3.33      ],
                       [2.31675601, 4.06579649, 2.45070669],
                       [2.17905675, 4.12697619, 2.06113431],
                       [2.03881733, 4.18103323, 1.91672726],
                       [1.89542713, 4.22493624, 1.85040208],
                       [1.74901085, 4.25696493, 1.80917537],
                       [1.60012767, 4.2760647 , 1.75218333],
                       [1.44968824, 4.28141842, 1.67812515],
                       [1.29897553, 4.27193666, 1.55618919],
                       [1.14974319, 4.24625308, 1.47000148],
                       [1.00541145, 4.20231238, 1.42825894],
                       [0.8687067 , 4.13871455, 1.41212167],
                       [0.74333962, 4.05597909, 1.43256548],
                       [0.63205355, 3.95554218, 1.46620311],
                       [0.53658858, 3.83990681, 1.52545747],
                       [0.45808266, 3.71192532, 1.60273681],
                       [0.39663789, 3.57462217, 1.69527018],
                       [0.35161547, 3.43076104, 1.80679323],
                       [0.32190117, 3.28274549, 1.94227008],
                       [0.3060057 , 3.13254586, 2.10856855],
                       [0.30219644, 2.98156312, 2.2     ],
                       [0.30866329, 2.83066357, 2.3     ]]

        ################## INPUT PARAMETERS ###################

        # Read all input parameters
        all_wheels_on_track = params['all_wheels_on_track']
        x = params['x']
        y = params['y']
        distance_from_center = params['distance_from_center']
        is_left_of_center = params['is_left_of_center']
        heading = params['heading']
        progress = params['progress']
        steps = params['steps']
        speed = params['speed']
        steering_angle = params['steering_angle']
        track_width = params['track_width']
        waypoints = params['waypoints']
        closest_waypoints = params['closest_waypoints']
        is_offtrack = params['is_offtrack']

        ############### OPTIMAL X,Y,SPEED,TIME ################

        # Get closest indexes for racing line (and distances to all points on racing line)
        closest_index, second_closest_index = closest_2_racing_points_index(
            racing_track, [x, y])

        # Get optimal [x, y, speed, time] for closest and second closest index
        optimals = racing_track[closest_index]
        optimals_second = racing_track[second_closest_index]

        # Save first racingpoint of episode for later
        if self.verbose == True:
            self.first_racingpoint_index = 0 # this is just for testing purposes
        if steps == 1:
            self.first_racingpoint_index = closest_index

        ################ REWARD AND PUNISHMENT ################

        ## Define the default reward ##
        reward = 1

        ## Reward if car goes close to optimal racing line ##
        DISTANCE_MULTIPLE = 1
        dist = dist_to_racing_line(optimals[0:2], optimals_second[0:2], [x, y])
        distance_reward = max(1e-3, 1 - (dist/(track_width*0.5)))
        reward += distance_reward * DISTANCE_MULTIPLE

        ## Reward if speed is close to optimal speed ##
        SPEED_DIFF_NO_REWARD = 1
        SPEED_MULTIPLE = 2
        speed_diff = abs(optimals[2]-speed)
        if speed_diff <= SPEED_DIFF_NO_REWARD:
            # we use quadratic punishment (not linear) bc we're not as confident with the optimal speed
            # so, we do not punish small deviations from optimal speed
            speed_reward = (1 - (speed_diff/(SPEED_DIFF_NO_REWARD))**2)**2
        else:
            speed_reward = 0
        reward += speed_reward * SPEED_MULTIPLE

        # Reward if less steps
        # REWARD_PER_STEP_FOR_FASTEST_TIME = 1
        # STANDARD_TIME = 37
        # FASTEST_TIME = 27
        # times_list = [row[3] for row in racing_track]
        # projected_time = projected_time(self.first_racingpoint_index, closest_index, steps, times_list)
        # try:
        #     steps_prediction = projected_time * 15 + 1
        #     reward_prediction = max(1e-3, (-REWARD_PER_STEP_FOR_FASTEST_TIME*(FASTEST_TIME) /
        #                                    (STANDARD_TIME-FASTEST_TIME))*(steps_prediction-(STANDARD_TIME*15+1)))
        #     steps_reward = min(REWARD_PER_STEP_FOR_FASTEST_TIME, reward_prediction / steps_prediction)
        # except:
        #     steps_reward = 0
        # reward += steps_reward

        # Zero reward if obviously wrong direction (e.g. spin)
        direction_diff = racing_direction_diff(
            optimals[0:2], optimals_second[0:2], [x, y], heading)
        if direction_diff > 30:
            reward = 1e-3
            
        # Zero reward of obviously too slow
        speed_diff_zero = optimals[2]-speed
        if speed_diff_zero > 0.5:
            reward = 1e-3
            
        ## Incentive for finishing the lap in less steps ##
        REWARD_FOR_FASTEST_TIME = 1500 # should be adapted to track length and other rewards
        STANDARD_TIME = 37  # seconds (time that is easily done by model)
        FASTEST_TIME = 27  # seconds (best time of 1st place on the track)
        if progress == 100:
            finish_reward = max(1e-3, (-REWARD_FOR_FASTEST_TIME /
                      (15*(STANDARD_TIME-FASTEST_TIME)))*(steps-STANDARD_TIME*15))
        else:
            finish_reward = 0
        reward += finish_reward
        
        ## Zero reward if off track ##
        if all_wheels_on_track == False:
            reward = 1e-3

        ####################### VERBOSE #######################
        
        if self.verbose == True:
            print("Closest index: %i" % closest_index)
            print("Distance to racing line: %f" % dist)
            print("=== Distance reward (w/out multiple): %f ===" % (distance_reward))
            print("Optimal speed: %f" % optimals[2])
            print("Speed difference: %f" % speed_diff)
            print("=== Speed reward (w/out multiple): %f ===" % speed_reward)
            print("Direction difference: %f" % direction_diff)
            print("Predicted time: %f" % projected_time)
            print("=== Steps reward: %f ===" % steps_reward)
            print("=== Finish reward: %f ===" % finish_reward)
            
        #################### RETURN REWARD ####################
        
        # Always return a float value
        return float(reward)


reward_object = Reward() # add parameter verbose=True to get noisy output for testing


def reward_function(params):
    return reward_object.reward_function(params)
