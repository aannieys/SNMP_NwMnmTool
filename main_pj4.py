from pysnmp.hlapi import * # to interact with SNMP agents.
import tkinter as tk # GUI library
from tkinter import ttk, messagebox

# Global variables to manage pagination
last_oid = None
current_display_index = 0  # Start with the first record
max_repetitions = 10  # Fetch 10 records at a time

# SNMP Operations
def snmp_get_next(target, community, oid):
    global last_oid
    results = []
    
    try:
        # If last_oid is None (first click), use the provided OID
        start_oid = last_oid if last_oid else oid
        
        print(f"Fetching next for OID: {start_oid}")  # Debugging: Print the current OID being used
        
        # Fetch next OID using nextCmd
        for errorIndication, errorStatus, errorIndex, varBinds in nextCmd(
            SnmpEngine(),
            CommunityData(community),
            UdpTransportTarget((target, 161)),
            ContextData(),
            ObjectType(ObjectIdentity(start_oid)),
            lexicographicMode=True  # Ensure lexicographical mode is enabled
        ):
            if errorIndication:
                messagebox.showerror("Error", f"SNMP Error: {errorIndication}")
                break
            elif errorStatus:
                messagebox.showerror("Error", f"SNMP Error: {errorStatus.prettyPrint()}")
                break
            else:
                # Process the next OID and value to extracts OID and value from the SNMP response.
                for varBind in varBinds:
                    oid, value = varBind
                    oid_name = oid.prettyPrint().split('.')[-1]  # Extract name from OID
                    oid_full = str(oid)  # The OID in full string format
                    ip_port = f"{target}:161"  # Assuming port 161 for SNMP
                    
                    # Check and decode the value properly => decode the value based on its type
                    if isinstance(value, IpAddress):
                        decoded_value = value.prettyPrint()  # Properly decode IP address
                    elif isinstance(value, bytes):
                        decoded_value = ".".join(map(str, value))  # Decode bytes as dotted-decimal
                    else:
                        decoded_value = str(value)
                    
                    value_type = type(value).__name__
                    name_oid = f"{oid_name} ({oid_full})"
                    results.append((name_oid, decoded_value, value_type, ip_port)) # store results
                    last_oid = oid_full  # Track the OID for subsequent calls

                # Break after fetching one result
                break
        
        if not results:
            print("No more results found.")
        
    except Exception as e:
        messagebox.showerror("Error", f"Unexpected error: {str(e)}")
    
    return results

def snmp_get_bulk(target, community, oid):
    global last_oid, max_repetitions
    results = []

    try:
        # Use the last fetched OID, or start from the given OID
        start_oid = last_oid if last_oid else oid
        print(f"Fetching bulk for OID: {start_oid}")  # Debugging: Print the current OID being used

        count = 0  # Track the number of records fetched in this call
        for errorIndication, errorStatus, errorIndex, varBinds in bulkCmd(
            SnmpEngine(),
            CommunityData(community),
            UdpTransportTarget((target, 161)),
            ContextData(),
            0, max_repetitions,  # Fetch up to max_repetitions entries
            ObjectType(ObjectIdentity(start_oid)),
            lexicographicMode=True
        ):
            if errorIndication:
                messagebox.showerror("Error", f"SNMP Error: {errorIndication}")
                break
            elif errorStatus:
                messagebox.showerror("Error", f"SNMP Error: {errorStatus.prettyPrint()}")
                break
            else:
                for varBind in varBinds:
                    oid, value = varBind
                    oid_name = oid.prettyPrint().split('.')[-1]  # Extract name from OID
                    oid_full = str(oid)  # Full OID as string
                    ip_port = f"{target}:161"  # SNMP target IP and port
                    
                    # Format value based on its type
                    if isinstance(value, IpAddress):
                        decoded_value = value.prettyPrint()  # Decode IP address
                    elif isinstance(value, bytes):
                        decoded_value = ".".join(map(str, value))  # Decode bytes as dotted-decimal
                    else:
                        decoded_value = str(value)  # Default string conversion
                    
                    value_type = type(value).__name__  # Type of the value
                    name_oid = f"{oid_name} ({oid_full})"  # Combine name and full OID
                    
                    results.append((name_oid, decoded_value, value_type, ip_port))

                    # Update the last_oid to this OID for the next call
                    last_oid = oid_full

                    count += 1
                    if count >= max_repetitions:
                        break  # Stop fetching after max_repetitions records

            if count >= max_repetitions:
                break  # Stop fetching if we've reached the max limit

        if not results:
            print("No more results found.")

    except Exception as e:
        messagebox.showerror("Error", f"Unexpected error: {str(e)}")
        print(f"Unexpected error: {str(e)}")  # Debugging

    return results

# GUI Functions
def populate_table(tree, data): # updates the table with fetched SNMP data
    """Populate the table with SNMP results."""
    for row in data:
        tree.insert("", tk.END, values=row)


def clear_table(tree):
    """Clear the table."""
    for i in tree.get_children():
        tree.delete(i)


def set_oid(entry_oid, oid):
    """Set the OID entry field to the selected OID."""
    if oid:
        entry_oid.delete(0, tk.END)
        entry_oid.insert(0, oid)


def handle_tree_selection(tree, entry_oid, table):
    """Handle tree selection for OID display and table population."""
    selected_item = tree.focus()
    item_data = tree.item(selected_item)
    oid = item_data["values"][0] if "values" in item_data and item_data["values"] else None
    if oid:
        set_oid(entry_oid, oid)
        clear_table(table)  # Clear table when a new OID is selected
        global last_oid, current_index
        last_oid = oid  # Update last_oid when a new OID is selected
        current_index = 0  # Reset current index for the new OID
        print(f"New OID selected: {last_oid}")  # Debugging: Print the selected OID


# Main Function
def main():
    root = tk.Tk()
    root.title("MIB Project 4")
    root.geometry("1200x800")

    frame_left = tk.Frame(root, width=300, bg="lightgray")
    frame_left.pack(side="left", fill="y")

    frame_right = tk.Frame(root)
    frame_right.pack(side="right", fill="both", expand=True)

    # OID Tree
    tree = ttk.Treeview(frame_left)
    tree.pack(fill="both", expand=True)
    tree.heading("#0", text="OID Tree", anchor="w")

    # Hardcoded OID Tree
    system_node = tree.insert("", "end", text="System", open=True, values=("1.3.6.1.2.1.1"))
    tree.insert(system_node, "end", text="sysDescr", values=("1.3.6.1.2.1.1.1"))
    tree.insert(system_node, "end", text="sysObjectID", values=("1.3.6.1.2.1.1.2"))
    tree.insert(system_node, "end", text="sysUpTime", values=("1.3.6.1.2.1.1.3"))
    tree.insert(system_node, "end", text="sysContact", values=("1.3.6.1.2.1.1.4"))
    tree.insert(system_node, "end", text="sysName", values=("1.3.6.1.2.1.1.5"))
    tree.insert(system_node, "end", text="sysLocation", values=("1.3.6.1.2.1.1.6"))
    tree.insert(system_node, "end", text="sysServices", values=("1.3.6.1.2.1.1.7"))

    ip_node = tree.insert("", "end", text="IP", open=True, values=("1.3.6.1.2.1.4"))
    tree.insert(ip_node, "end", text="ipForwarding", values=("1.3.6.1.2.1.4.1"))
    tree.insert(ip_node, "end", text="ipDefaultTTL", values=("1.3.6.1.2.1.4.2"))
    tree.insert(ip_node, "end", text="ipInReceives", values=("1.3.6.1.2.1.4.3"))
    tree.insert(ip_node, "end", text="ipInHdrErrors", values=("1.3.6.1.2.1.4.4"))
    tree.insert(ip_node, "end", text="ipInAddrErrors", values=("1.3.6.1.2.1.4.5"))
    tree.insert(ip_node, "end", text="ipForwDatagrams", values=("1.3.6.1.2.1.4.6"))
    tree.insert(ip_node, "end", text="ipInUnknownProtos", values=("1.3.6.1.2.1.4.7"))
    tree.insert(ip_node, "end", text="ipInDiscards", values=("1.3.6.1.2.1.4.8"))
    tree.insert(ip_node, "end", text="ipInDelivers", values=("1.3.6.1.2.1.4.9"))
    tree.insert(ip_node, "end", text="ipOutRequests", values=("1.3.6.1.2.1.4.10"))
    tree.insert(ip_node, "end", text="ipOutDiscards", values=("1.3.6.1.2.1.4.11"))
    tree.insert(ip_node, "end", text="ipOutNoRoutes", values=("1.3.6.1.2.1.4.12"))
    tree.insert(ip_node, "end", text="ipReasmTimeout", values=("1.3.6.1.2.1.4.13"))
    ip_route_table = tree.insert(ip_node, "end", text="ipRouteTable", open=True, values=("1.3.6.1.2.1.4.21"))
    tree.insert(ip_route_table, "end", text="ipRouteDest", values=("1.3.6.1.2.1.4.21.1.1"))
    tree.insert(ip_route_table, "end", text="ipRouteIfIndex", values=("1.3.6.1.2.1.4.21.1.2"))
    tree.insert(ip_route_table, "end", text="ipRouteMetric1", values=("1.3.6.1.2.1.4.21.1.3"))
    tree.insert(ip_route_table, "end", text="ipRouteNextHop", values=("1.3.6.1.2.1.4.21.1.4"))
    tree.insert(ip_route_table, "end", text="ipRouteType", values=("1.3.6.1.2.1.4.21.1.7"))
    tree.insert(ip_route_table, "end", text="ipRouteProto", values=("1.3.6.1.2.1.4.21.1.8"))
    tree.insert(ip_route_table, "end", text="ipRouteAge", values=("1.3.6.1.2.1.4.21.1.9"))
    tree.insert(ip_route_table, "end", text="ipRouteMask", values=("1.3.6.1.2.1.4.21.1.11"))

    udp_node = tree.insert("", "end", text="UDP", open=True, values=("1.3.6.1.2.1.7"))
    tree.insert(udp_node, "end", text="udpInDatagrams", values=("1.3.6.1.2.1.7.1"))
    tree.insert(udp_node, "end", text="udpNoPorts", values=("1.3.6.1.2.1.7.2"))
    tree.insert(udp_node, "end", text="udpInErrors", values=("1.3.6.1.2.1.7.3"))
    tree.insert(udp_node, "end", text="udpOutDatagrams", values=("1.3.6.1.2.1.7.4"))
    tree.insert(udp_node, "end", text="udpTable", values=("1.3.6.1.2.1.7.5"))

    # Right Panel
    frame_top = tk.Frame(frame_right)
    frame_top.pack(side="top", fill="x", padx=10, pady=10)

    tk.Label(frame_top, text="Target:").grid(row=0, column=0, padx=5, pady=5)
    entry_target = tk.Entry(frame_top, width=20)
    entry_target.grid(row=0, column=1, padx=5, pady=5)
    entry_target.insert(0, "127.0.0.1")

    tk.Label(frame_top, text="Community:").grid(row=0, column=2, padx=5, pady=5)
    entry_community = tk.Entry(frame_top, width=20)
    entry_community.grid(row=0, column=3, padx=5, pady=5)
    entry_community.insert(0, "public")

    tk.Label(frame_top, text="OID:").grid(row=0, column=4, padx=5, pady=5)
    entry_oid = tk.Entry(frame_top, width=20)
    entry_oid.grid(row=0, column=5, padx=5, pady=5)

    # Operation Dropdown
    operation_var = tk.StringVar(value="Get Next")
    operation_menu = ttk.Combobox(frame_top, textvariable=operation_var, values=["Get Next", "Get Bulk"], width=15)
    operation_menu.grid(row=0, column=8, padx=5, pady=5)

    # Execute Button
    tk.Button(frame_top, text="Go", command=lambda: populate_table(
        table, snmp_get_next(entry_target.get(), entry_community.get(), entry_oid.get())
        if operation_var.get() == "Get Next" else snmp_get_bulk(entry_target.get(), entry_community.get(), entry_oid.get())
    )).grid(row=0, column=9, padx=5, pady=5)

    # Clear Table Button
    tk.Button(frame_top, text="Clear Table", command=lambda: clear_table(table)).grid(row=0, column=10, padx=5, pady=5)

    frame_table = tk.Frame(frame_right)
    frame_table.pack(fill="both", expand=True)

    table_scroll_y = tk.Scrollbar(frame_table, orient="vertical")
    table_scroll_y.pack(side="right", fill="y")

    table_scroll_x = tk.Scrollbar(frame_table, orient="horizontal")
    table_scroll_x.pack(side="bottom", fill="x")

    table = ttk.Treeview(frame_table, columns=("Name/OID", "Value", "Type", "IP:Port"), show="headings")
    table.pack(fill="both", expand=True)

    table_scroll_y.config(command=table.yview)
    table_scroll_x.config(command=table.xview)

    table.heading("Name/OID", text="Name/OID")
    table.heading("Value", text="Value")
    table.heading("Type", text="Type")
    table.heading("IP:Port", text="IP:Port")

    tree.bind("<<TreeviewSelect>>", lambda e: handle_tree_selection(tree, entry_oid, table))

    root.mainloop()

if __name__ == "__main__":
    main()