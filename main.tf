resource "digitalocean_ssh_key" "default" {
    name = "sshkey"
    public_key = file("~/.ssh/id_ed25519.pub")
}

resource "digitalocean_droplet" "scrapyd" {
    count = length(var.nodes)
    name = var.nodes[count.index]
    image = "ubuntu-22-04-x64"
    region = "blr1"
    size = "s-1vcpu-1gb"
    ssh_keys = [digitalocean_ssh_key.default.fingerprint]
}

resource "digitalocean_droplet" "db" {
    name = "db"
    image = "ubuntu-22-04-x64"
    region = "blr1"
    size = "s-1vcpu-1gb"
    ssh_keys = [digitalocean_ssh_key.default.fingerprint]
}

output "scrapyd-public-ips" {
  value = [for ins in digitalocean_droplet.scrapyd: ins.ipv4_address]
  description = "Ip addresses for scrapyd servers"
}

output "db-ip" {
  value = digitalocean_droplet.db.ipv4_address
  description = "Ip address for db server"
}

