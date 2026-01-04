import uuid

# In-memory store for MVP
_contacts_store = [
    {"id": "1", "name": "Alice Smith", "email": "alice@example.com", "phone": "555-0101"},
    {"id": "2", "name": "Bob Jones", "email": "bob@example.com", "phone": "555-0102"}
]

def register(kernel):
    kernel["log"]("Dhii-Contacts plugin loading...")

    async def fetch_contacts(params):
        kernel["log"]("Dhii-Contacts: Fetching contacts...")
        
        query = params.get("query", "").lower()
        
        filtered = [
            c for c in _contacts_store 
            if query in c["name"].lower() or query in c["email"].lower()
        ]
        
        # Sort by name
        filtered.sort(key=lambda x: x["name"])
        
        items = []
        for contact in filtered:
            items.append({
                "id": contact["id"],
                "title": contact["name"],
                "subtitle": f"{contact['email']} | {contact['phone']}",
                "action": {
                    "type": "view_details",
                    "params": {"contact_id": contact["id"]}
                }
            })
            
        if not items:
             items.append({"type": "text", "content": "No contacts found."})
        
        return {
            "type": "card",
            "id": "contacts-list",
            "title": "Contacts",
            "children": [
                {
                    "type": "list",
                    "items": items
                },
                {
                    "type": "button",
                    "label": "Add Contact",
                    "action": {
                        "type": "form",
                        "form_id": "add_contact_form"
                    }
                }
            ]
        }

    async def add_contact(params):
        kernel["log"](f"Dhii-Contacts: Adding contact '{params.get('name')}'...")
        
        name = params.get("name")
        email = params.get("email", "")
        phone = params.get("phone", "")
        
        if not name:
             return {"type": "card", "title": "Error", "children": [{"type": "text", "content": "Name is required."}]}
             
        new_contact = {
            "id": str(uuid.uuid4()),
            "name": name,
            "email": email,
            "phone": phone
        }
        
        _contacts_store.append(new_contact)
        
        return {
            "type": "card",
            "title": "Contact Added",
            "children": [
                {"type": "text", "content": f"Successfully added: {name}"},
                {"type": "text", "content": f"Email: {email}"}
            ]
        }

    kernel["register_capability"]("fetch_contacts", fetch_contacts)
    kernel["register_capability"]("add_contact", add_contact)
    kernel["log"]("Dhii-Contacts: Capabilities registered.")
