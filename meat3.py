try:
	from Tkinter import *
	import tkFileDialog as file_dialog
	from Tkinter import ttkexcept ImportError:
	from tkinter import *
	from tkinter import filedialog as file_dialog
	from tkinter import ttk
	import xml.etree.cElementTree as ET
import os, sys, subprocess, signal, socket, time

###################################
#
#          M A C R O S
#
###################################

NUM_OF_CONFIGURABLE_ELEMENTS = 2

NUM_NETWORK_CONFIGURATIONS  =  7

NUM_SCENARIO_CONFIGURATIONS =  3 

NUM_TRAFFIC_CONFIGURATIONS = 4

MAX_NUMBER_OF_USER_ENTERED_SCENARIOS = 3	

LOGIN_CMD="root@10.248.13.9"

MEAT_CMD = ""

ITU_I_NETWORK = 10
ANSI_NETWORK  = 11

###################################
#
#        G L O B A L S
#
##################################

root = Tk()

root.title("MEAT Traffic Simulator")

root.geometry("800x536")

#Disable resizing of the MEAT GUI window.
root.resizable(0,0)

tabControl = ttk.Notebook(root)                                   # Create Tab Control

welcomeTab = ttk.Frame(tabControl)                                # Create a tab 
loadMessageTab = ttk.Frame(tabControl)                            # Create a tab 
networkConfigTab = ttk.Frame(tabControl)                          # Create a tab 
scenarioConfigTab = ttk.Frame(tabControl)                         # Create a tab 

tabControl.add(welcomeTab, text='Welcome Page')                   # Add the tab
tabControl.add(loadMessageTab, text='Load Message')               # Add the tab
tabControl.add(networkConfigTab, text='Network Configuration')    # Add the tab
tabControl.add(scenarioConfigTab, text='Scenario Configuration')  # Add the tab

tabControl.grid(row=3, padx=2, pady=2, sticky='W')                # Pack to make visible

##################################
#	INTEGER GLOBAL VARIABLES
##################################
number_of_added_scenarios = 0

#Value of this variable is fixed as per layout. If the layout
#changes, this value will have to be adjusted as well.
scenario_row_count = 13

count_call_2_file_write_API = 0;

scenario_name = "";

g_traffic_flavour = ""

g_network_sig_id=""

##################################
#	BOOLEAN GLOBAL VARIABLES
##################################
button_already_created=False

##################################
#	STRING GLOBAL VARIABLES
##################################
load_message_name = ""

msgNameInScenario = ""

##################################
#	LIST GLOBAL VARIABLES
##################################
list_of_scenario_dicts = []

list_of_traffic_config_labels = []

dynamic_trafic_configuration = [0,0,0,0]

network_and_scenario =  [

						("scenario_"),

						("network_"),

						]


						
network_configuration = [

						("Meat IP:"),

						("Meat port:"),

						("IPSG Point code:"),

						("IPSG IP:"),

						("IPSG port:"),

						("Eagle SID:"),

						("Routing Context:"),

						]						

network_config_values = [0,0,0,0,0,0,0]



scenario_configuration = [

						 ("Scenario message name:"),

						 ("Delay median:"),

						 ("Deviation:"),

                         ]

scenario_config_values = [0,0,0]   



traffic_configuration =  [
						 ("Message count:"),
						 ("Scenario name:"),
						 ("Traffic delay:"),
						 ("Traffic duration:"),
						 ]

traffic_config_values = [0,0,0,0]

##################################
#	DICTIONARY GLOBAL VARIABLES
##################################
network_dict = dict(zip(network_configuration, network_config_values));
traffic_dict = dict(zip(traffic_configuration, traffic_config_values));


########################################
#
#    F U N C T I O N S / M E T H O D S
#
########################################

def runMeatTraffic():
	try:
		meat_process_id = subprocess.Popen(["plink", "%s" % LOGIN_CMD, "-pw", "NextGen", MEAT_CMD],
											shell=False,
											stdout=subprocess.PIPE,
											stderr=subprocess.PIPE)
		
		time.sleep(15.0)	
		meat_process_id.kill()
		
	except Exception:
		boot = Tk()
		boot.title("Error Message")
		boot.geometry("400x100")
	
		failure_message = "Could not run traffic!"
		
		Label(boot, text=failure_message, fg="red", font=("Helvetica", 10), justify=CENTER).grid(pady=5)
		button = Button(boot, text="Ok", width=10, command=lambda: exitWindow(boot))
		button.grid(pady=30, padx=150)
		boot.eval('tk::PlaceWindow %s center' % boot.winfo_pathname(boot.winfo_id()))
	finally:
		pass


def stopMeatTraffic():

	#Command to be executed:->
	#ps -ef | grep network_GURWUNI5F3171 | grep -v grep | awk '{print $2}' | xargs kill
	kill_cmd = "ps -ef | grep "+socket.gethostname()+" | grep -v grep | awk '{print $2}' | xargs kill"

	try:
		kill_meat_process = subprocess.Popen(["plink", "%s" % LOGIN_CMD, "-pw", "NextGen", kill_cmd],
											 shell=False,
											 stdout=subprocess.PIPE,
											 stderr=subprocess.PIPE)
	except Exception:
		boot = Tk()
		boot.title("Error Message")
		boot.geometry("400x100")
	
		failure_message = "No running traffic process to stop!"
		
		Label(boot, text=failure_message, fg="red", font=("Helvetica", 10), justify=CENTER).grid(pady=5)
		button = Button(boot, text="Ok", width=10, command=lambda: exitWindow(boot))
		button.grid(pady=30, padx=150)
		boot.eval('tk::PlaceWindow %s center' % boot.winfo_pathname(boot.winfo_id()))
	finally:
		pass

							
#This function sends all XML files (message.xml, network.xml and
#scenario.xml) to the remote server where MEAT is residing.
def send_file_to_server(local_directory, remote_folder):
	
	global count_call_2_file_write_API
	
	#Get username, ip address and path of the remote MEAT server
	remote_path = "root@10.248.13.9:/root"+remote_folder
	
	#Build pscp command that will put the XML file on the remote path
	pscp_command = "pscp -pw NextGen "+ local_directory + " " + remote_path
	
	# Correct pscp command format:->
	# pscp -pw NextGen local_directory remote_path

	#Check if pscp command was successful. If it failed, let the user 
	#know that something went wrong.
	if (os.system(pscp_command) != 0):
		#Maximum number of scenarios added by user. Therefore, every time
		#the 'Add Scenario' button is pressed, show a small window informing the
		#user that max limit of additional scenarios has been reached.
		boot = Tk()
		boot.title("Error Message")
		boot.geometry("400x100")
	
		failure_message = "File write to remote server unsuccessful."
		
		Label(boot, text=failure_message, fg="red", font=("Helvetica", 10), justify=CENTER).grid(pady=5)
		button = Button(boot, text="Ok", width=10, command=lambda: exitWindow(boot))
		button.grid(pady=30, padx=150)
		boot.eval('tk::PlaceWindow %s center' % boot.winfo_pathname(boot.winfo_id()))
		
	count_call_2_file_write_API+=1
	
	#Check if all three XML files have been sent to remote server.
	#If they have, cross the final frontier and run the MEAT command
	#to run traffic.
	if (count_call_2_file_write_API == 3):
		runMeatTraffic()
		count_call_2_file_write_API = 0
		


#This function formats the xml file properly to increase readability.
def indent(elem, level=0):

  i = "\n" + level*"  "

  if len(elem):

    if not elem.text or not elem.text.strip():

      elem.text = i + "  "

    if not elem.tail or not elem.tail.strip():

      elem.tail = i

    for elem in elem:

      indent(elem, level+1)

    if not elem.tail or not elem.tail.strip():

      elem.tail = i

  else:

    if level and (not elem.tail or not elem.tail.strip()):

      elem.tail = i

	  
#This function contains backend code for 'Browse' button. 
def browsefunc(root, message_entry_widget):

	temp_path_list = []

	global load_message_name
	
	#Make browse button work and ask for path to file.

	message_xml = file_dialog.askopenfilename()
	
	message_entry_widget.delete(0,END)
	message_entry_widget.insert(0, message_xml)
	
	load_message_name = message_xml

	
#This function generates network and scenario files based on the user-entered
#configuration in the entry widgets. 
def generateXMLs():
	global MEAT_CMD
	
	element_loop = 0

	network_loop = 0;

	scenario_loop = 0;

	list_of_user_entries_nw = []
	list_of_user_entries_scen = []
	list_of_user_entries_traffic = []


	#Get the user-entered network configuration into a list.

	#We are going to use this list in generating XML with entered network config later on.

	for item in network_dict.keys():

		list_of_user_entries_nw.append(network_dict[item].get())

	#Get the user-entered traffic configuration into a list.
	#We are going to use this list in generating XML with entered traffic config later on.
	for item in traffic_dict.keys():
		list_of_user_entries_traffic.append(traffic_dict[item].get())


	#Get current path of the source file
	current_directory = os.path.dirname(os.path.realpath(__file__))
	
	current_directory
	
	temp_list = load_message_name.split('/')
	
	filename_from_local_path = temp_list[len(temp_list)-1]
	
	scenario_path_to_load_message = "../Messages/meatgui/"+filename_from_local_path


	#There are two elements that we need to generate XML for:
	#Network and Scenario.

	while(element_loop < NUM_OF_CONFIGURABLE_ELEMENTS):

		#Create filename for the XML

		filename = network_and_scenario[element_loop]+socket.gethostname()+ ".xml"

		#If the file is network config, use the list created above to 
		#build local and remote network subelements.

		if "network" in filename:

			MEAT_CMD += (" -n ./Network/"+filename)
		
			#Begin building the elements and subelements for the network config XML file.

			peers_elem = ET.Element("peers")

			stream_id_subelem = ET.SubElement(peers_elem, "stream id=\"0\"")

			asp_id_subelem = ET.SubElement(peers_elem, "asp id=\"1\"")

			sgp_id_subelem = ET.SubElement(peers_elem, "sgp id=\"1\"")

			signalling_id_subelem = ET.SubElement(peers_elem, "signaling id=\"{}\"".format(g_network_sig_id))

			local_network = "local ip=\""+list_of_user_entries_nw[0]+"\" port=\""+list_of_user_entries_nw[1]+"\" pc=\""+list_of_user_entries_nw[2]+ "\" forceSLS=\"yes\" force=\"yes\" mode=\"AS\""

			remote_network = "remote ip=\""+list_of_user_entries_nw[3]+"\" port=\""+list_of_user_entries_nw[4]+"\" pc=\""+list_of_user_entries_nw[5]+ "\" force=\"yes\""	

			ET.SubElement(peers_elem, local_network)

			ET.SubElement(peers_elem, remote_network)

			ET.SubElement(peers_elem, "routingcontext", rc=list_of_user_entries_nw[6])

			#Pretty print the XML contents into the XML file
			indent(peers_elem)

			#Create an ElementTree in the network config XML file for the given element and
			#write to all elements to the XML file.
			tree = ET.ElementTree(peers_elem)


		#If the file is scenario config, use the list created above to 
		#build scenario elements.

		elif "scenario" in filename:

			MEAT_CMD = "meat -s ./Scenario/"+filename
		
			#Begin building the elements and subelements for the network config XML file.

			scenario_xml_elem = ET.Element("generator")

			message_struct_elem = ET.SubElement(scenario_xml_elem, "messageStructure")

			include_subelem = ET.SubElement(message_struct_elem, "include", src=scenario_path_to_load_message)

			message_name_subelem = ET.SubElement(message_struct_elem, "message", name=msgNameInScenario.get())

			variable_subelem = ET.SubElement(message_name_subelem, "variables")

			global_vars_subelem = ET.SubElement(scenario_xml_elem, "globalVariables")				

			while(scenario_loop < number_of_added_scenarios):

				temp_list = []

				#Get the user-entered network configuration into a list.

				#We are going to use this list in generating XML with entered network config later on.

				for config_value in list_of_scenario_dicts[scenario_loop].values():

					temp_list.append(config_value.get())

					

				list_of_user_entries_scen.append(temp_list)


				scenario_subelem = ET.SubElement(scenario_xml_elem, "scenario", name="Scenario "+str(scenario_loop+1))

				sequence_subelem = ET.SubElement(scenario_subelem, "sequence")

				useMessage_subelem = ET.SubElement(sequence_subelem, "useMessage", name=list_of_user_entries_scen[scenario_loop][0])

				scenario_config = "delay median=\"" +list_of_user_entries_scen[scenario_loop][1] + "\" deviation=\"" + list_of_user_entries_scen[scenario_loop][2] + "\" distribution=\"normal\""

				ET.SubElement(useMessage_subelem, scenario_config)
				scenario_loop+=1



			traffic_subelem = ET.SubElement(scenario_xml_elem, "traffic", flavor=g_traffic_flavour)
			traffic_scenario = "useScenario name=\""+list_of_user_entries_traffic[1]+"\" count=\""+list_of_user_entries_traffic[0]+"\" delay=\""+list_of_user_entries_traffic[3]+ "\" duration=\""+list_of_user_entries_traffic[2]+"\""
			useScenario_subelem = ET.SubElement(traffic_subelem, traffic_scenario)
		

			#Pretty print the XML contents into the XML file
			indent(scenario_xml_elem)

			#Create an ElementTree in the network config XML file for the given element.
			tree = ET.ElementTree(scenario_xml_elem)
			

		#Write to all elements to the XML file.
		tree.write(filename, encoding="UTF-8")

		#Get path to file on current directory
		current_path_to_file = current_directory+"\\"+filename


		#Put network.xml and scenario.xml at respective folders on 10.248.13.9 machine
		if "network" in filename:
			send_file_to_server(current_path_to_file, "/Network/")
		elif "scenario" in filename:
			send_file_to_server(current_path_to_file, "/Scenario/")

		element_loop+=1
	
	#Put message.xml in Messages folder on 10.248.13.9 machine
	send_file_to_server(load_message_name, "/Messages/meatgui/")
	
		
#This function populates the entry widgets for traffic configuration with
#user-entered configuration in the entry widgets. This is used for moving 
#traffic configuration to a new location when new scenarios are added.	
def addTrafficConfiguration(root, row_count, new_scenario_added):
	global list_of_traffic_config_labels
	global dynamic_trafic_configuration
	
	temp_list = []
	
	main_label = Label(root, text="Traffic Configuration:", font=("Helvetica", 10))
	
	list_of_traffic_config_labels.append(main_label)
	
	main_label.grid(row=row_count, padx=100, pady=2, sticky=W)

	loop_cnt = 0;

	while (loop_cnt < NUM_TRAFFIC_CONFIGURATIONS):

		component_label = Label(root, text=traffic_configuration[loop_cnt])
		
		list_of_traffic_config_labels.append(component_label)
		
		component_label.grid(row=row_count, padx=230, pady=2, sticky=W)
		
		traffic_dict[traffic_configuration[loop_cnt]] = Entry(root)

		if new_scenario_added == False:
			if (traffic_configuration[loop_cnt] == "Scenario name:"):
				traffic_dict[traffic_configuration[loop_cnt]].insert(0,scenario_name)
			else:
				traffic_dict[traffic_configuration[loop_cnt]].insert(0,"")
			
			traffic_dict[traffic_configuration[loop_cnt]].grid(row=row_count, padx=375, pady=2, sticky=W)
		else:
			traffic_dict[traffic_configuration[loop_cnt]].insert(0,dynamic_trafic_configuration[loop_cnt])
			traffic_dict[traffic_configuration[loop_cnt]].grid(row=row_count, padx=375, pady=2, sticky=W)
			
		row_count = row_count+1
		
		loop_cnt+=1
		
	return row_count

	
#This function removes the entry widgets for traffic configuration from their
#current location. This is used for moving traffic configuration to a new location
#when new scenarios are added.	
def removeTrafficConfiguration(root):

	#Destroy all label widgets created for traffic configuration.
	#We shall create them again later on.
	for item in list_of_traffic_config_labels:
		item.destroy()
		
	#Take a local loop counter.
	loop_cnt = 0;

	#Loop through all entry widgets, make a copy of their values for restoration
	#and then destroy the entry widgets themselves.
	while (loop_cnt < NUM_TRAFFIC_CONFIGURATIONS):
		#Store the current user-entered values for traffic configuration before
		#destroying the widget so as to restore these values when same widgets are
		#created at a different location.
		dynamic_trafic_configuration[loop_cnt] = (traffic_dict[traffic_configuration[loop_cnt]].get())
		
		#Destroy the entry widget.
		traffic_dict[traffic_configuration[loop_cnt]].destroy()

		#Increment loop counter.
		loop_cnt+=1
		

#This function is called from addScenario function when the 'Add Scenario' button 
#is clicked. It manages the placement of the 'Run MEAT Traffic' button as well as the
#placement of the traffic configuration widgets.
def addScenarioButton(root):
	global run_button, stop_button
	global button_already_created
	global scenario_row_count
	
	#If the 'Run Meat Traffic' button is already created, and the
	#'Add Scenario' button is pressed again, we need to shift the 
	#'Run Meat Traffic' button below to accomodate new scenario config.
	if (button_already_created == 0):

		scenario_row_count = addTrafficConfiguration(root, scenario_row_count, button_already_created);
		
		run_button = Button(root, text = "Run MEAT traffic", command=generateXMLs)

		run_button.grid(row=scenario_row_count, padx=150, pady=10, sticky=W+S)
		
		stop_button = Button(root, text = "Stop MEAT traffic", command=stopMeatTraffic)

		stop_button.grid(row=scenario_row_count, padx=270, pady=10, sticky=W+S)

		button_already_created = True

	else:

		removeTrafficConfiguration(root);
		
		run_button.destroy()
		stop_button.destroy()
		
		scenario_row_count = addTrafficConfiguration(root, scenario_row_count, button_already_created);

		run_button = Button(root, text = "Run MEAT traffic", command=generateXMLs)

		run_button.grid(row=scenario_row_count, padx=150, pady=10, sticky=W+S)
		
		stop_button = Button(root, text = "Stop MEAT traffic", command=stopMeatTraffic)

		stop_button.grid(row=scenario_row_count, padx=270, pady=10, sticky=W+S)

		button_already_created = True
		

#This function is called to exit 'Errow Window' that is generated when user tries
#to enter more than allowed number of scenario configurations.		
def exitWindow(window):
	window.destroy();


#This function is triggered when the 'Add Scenario' button is clicked. It creates
#new widgets for user to enter scenario configuration in.
def addScenario(root):

	global scenario_row_count
	global scenario_name

	global number_of_added_scenarios

	if (number_of_added_scenarios < MAX_NUMBER_OF_USER_ENTERED_SCENARIOS):
		scenario_dict = dict(zip(scenario_configuration, scenario_config_values));
		
		number_of_added_scenarios+=1; 
		
		scenario_name = "Scenario "+str(number_of_added_scenarios)
		
		Label(root, text=scenario_name+":", font=("Helvetica", 10)).grid(row=scenario_row_count, padx=100, pady=2, sticky=W)
		
		loop_cnt = 0;
		
		while (loop_cnt < NUM_SCENARIO_CONFIGURATIONS):
		
			Label(root, text=scenario_configuration[loop_cnt]).grid(row=scenario_row_count, padx=230, pady=2, sticky=W)
			
			scenario_dict[scenario_configuration[loop_cnt]] = Entry(root)
			
			if (scenario_configuration[loop_cnt] == "Scenario message name:"):
				scenario_dict[scenario_configuration[loop_cnt]].insert(0,"isup_con")
			else:
				scenario_dict[scenario_configuration[loop_cnt]].insert(0,"")
			
			scenario_dict[scenario_configuration[loop_cnt]].grid(row=scenario_row_count, padx=375, pady=2, sticky=W)
			
			scenario_row_count = scenario_row_count+1
			
			loop_cnt+=1
		
		#Make a list of dictionaries to keep all the different scenario 
        
	    #configurations under the same roof. Based on which scenario radio button is 
        
	    #selected, we can index into the list and get our specific dictionary having a
        
	    #specific configuration.
		list_of_scenario_dicts.append(scenario_dict)
		
		addScenarioButton(root);
		
	else:
		#Maximum number of scenarios added by user. Therefore, every time
		#the 'Add Scenario' button is pressed, show a small window informing the
		#user that max limit of additional scenarios has been reached.
		boot = Tk()
		boot.title("Error Message")
		boot.geometry("400x100")
		
		Label(boot, text="Max limit of additional scenarios reached. Limit = 3", fg="red", font=("Helvetica", 10), justify=CENTER).grid(pady=5)
		button = Button(boot, text="Ok", width=10, command=lambda: exitWindow(boot))
		button.grid(pady=30, padx=150)
		boot.eval('tk::PlaceWindow %s center' % boot.winfo_pathname(boot.winfo_id()))
		

#This function is the parent function for every activity that has to be done to
#enable the user to configure one or more scenarios for running MEAT traffic.
def scenario_config(root):
	scenarioConfigFrame = LabelFrame(root, text="Scenario Configuration:", font=("Helvetica", 11, "bold"))
	
	#Entry widgets for configuring scenarios

	global msgNameInScenario

	global list_of_scenario_dicts

	scenarioConfigFrame.grid(row=4, padx=5, pady=5, sticky=W+S)
	
	Label(scenarioConfigFrame, text="Message Name:").grid(row=0, padx=100, pady=2,  sticky=W)

	msgNameInScenario = Entry(scenarioConfigFrame)
				
	msgNameInScenario.insert(0, "isup_con")

	msgNameInScenario.grid(row=0, padx=320, pady=2, sticky=W)

	Button(scenarioConfigFrame, text="Add scenario", command=lambda: addScenario(scenarioConfigFrame)).grid(row=1, padx=100, pady=2, sticky=W)


def selectNetwork(value):
	global g_traffic_flavour, g_network_sig_id

	if (value == ITU_I_NETWORK):
		g_traffic_flavour = "itui"
		g_network_sig_id  = "ITU-I"
	else:
		g_traffic_flavour = "ansi"
		g_network_sig_id  = "ANSI"
	
	
#This function is the parent function for every activity that has to be done to
#enable the user to configure network for running MEAT traffic.
def network_config(root):
	networkConfigFrame = LabelFrame(root, text="Network Configuration:", font=("Helvetica", 11, "bold"))
	
	networkConfigFrame.grid(row=3, padx=5, pady=5, sticky=W+S)

	#Entry widgets to enter IPs, ports and point codes

	loop_cnt = 0;

	global network_dict
	
	row_var = 1

	var = IntVar()
	var.set(10)

	Label(networkConfigFrame, text="Network Type:").grid(row=0, padx=100, pady=2, sticky=W)
	
	ansi_radio = Radiobutton(networkConfigFrame, text="ANSI", variable=var, value=ANSI_NETWORK, command=lambda: selectNetwork(ANSI_NETWORK))
	ansi_radio.grid(row=0, padx=250, pady=2,  sticky=W)
	itu_radio = Radiobutton(networkConfigFrame, text="ITU-I", variable=var, value=ITU_I_NETWORK, command=lambda: selectNetwork(ITU_I_NETWORK))
	itu_radio.grid(row=0, padx=300, pady=2,  sticky=W)


	while (loop_cnt < NUM_NETWORK_CONFIGURATIONS):

		Label(networkConfigFrame, text=network_configuration[loop_cnt]).grid(row=row_var, padx=100, pady=2, sticky=W)

		network_dict[network_configuration[loop_cnt]] = Entry(networkConfigFrame)
	
		#Initialize some of these labels with default values as they don't change in value
		#as frequently as the other labels.
		if (network_configuration[loop_cnt] == "Meat IP:"):
			network_dict[network_configuration[loop_cnt]].insert(0,"10.248.13.9")
		elif (network_configuration[loop_cnt] == "IPSG IP:"):
			network_dict[network_configuration[loop_cnt]].insert(0,"10.248.13.xxx")
		elif (network_configuration[loop_cnt] == "Routing Context:"):
			network_dict[network_configuration[loop_cnt]].insert(0,"10")
		elif (network_configuration[loop_cnt] == "Eagle SID:"):
			network_dict[network_configuration[loop_cnt]].insert(0,"1-1-1")
		else:
			network_dict[network_configuration[loop_cnt]].insert(0,"")

		network_dict[network_configuration[loop_cnt]].grid(row=row_var, padx=250, pady=2,  sticky=W)

		row_var = row_var+1

		loop_cnt+=1
		
		


#This function is the parent function for every activity that has to be done to
#enable the user to upload his message file that is to be used for running MEAT 
#traffic.
def load_message(root):
	loadMessageFrame = LabelFrame(root, text = "Load Message:", font=("Helvetica", 11, "bold"))

	#Create button to load custom message

	loadMessageFrame.grid(row=2, padx=5, pady=5, sticky=W+S)

	message_widget = Entry(loadMessageFrame, justify=LEFT, width=50)

	message_widget.insert(0, "Choose you message.xml")

	message_widget.grid(padx=100, row=0, pady=5, sticky=W+S)

	Button(loadMessageFrame, text = "Browse", command=lambda: browsefunc(root, message_widget)).grid(row=0, padx=440, pady=5, sticky=W+S)


#This function is responsible for printing out the headers of the tool which includes
#the name of the tool as well as some instructive text.
def welcome_text(root):
	welcomeFrame = LabelFrame(root, text="MEAT Configuration", font=("Helvetica", 12, 'bold'))

	welcome = '''This is a GUI tool for running messages via MEAT. Follow the steps below to run MEAT traffic:
  1) In 'Load Message' tab, load the message.xml you want to run.
  2) In 'Network Configuration' tab, add the network configuration you want.
  3) In 'Scenario Configuration' tab, add the scenario configuration(s) you want. Then click "Run MEAT traffic" to run the traffic.
  4) In case you want to stop the traffic prematurely, click the "Stop MEAT traffic" button.
  
  Some of the fields have been initialized with default values to make configuration a little bit faster and easier.'''
	
	welcomeFrame.grid(row=0, column=0, sticky=W, padx=5, pady=5)
	
	Label(welcomeFrame, text = welcome, justify=LEFT).grid(row=1, sticky=W, padx=5, pady=5)


#################################################
#
#     F I R S T   F U N C T I O N   C A L L S
#
#################################################

welcome_text(welcomeTab)

load_message(loadMessageTab)

network_config(networkConfigTab)

scenario_config(scenarioConfigTab)

		

#################################################
#
#       M A I N L O O P
#
#.Description: Everything starts here. This is 
#how to call the main function in Tkinter.
#################################################

root.mainloop()





###############
#    TO-DO
###############
# 1) Create an executible of this program







