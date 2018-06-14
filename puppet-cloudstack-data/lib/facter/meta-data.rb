
require 'facter'

ENV['PATH']='/bin:/sbin:/usr/bin:/usr/sbin'

# The dirs to search for the dhcp lease files in. Works for RHEL/CentOS and Ubuntu
dirs = ['/var/lib/dhclient', '/var/lib/dhcp3']

regex = Regexp.new(/dhclient.+lease/)

dirs.each do |lease_dir|
    if !File.directory? lease_dir
        next
    end

    Dir.entries(lease_dir).each do |file|
        result = regex.match(file)

        # Expand file back into the absolute path
        file = lease_dir + '/' + file

        if result && File.size?(file) != nil
            cmd = sprintf("grep dhcp-server-identifier %s | tail -1 | awk '{print $NF}' | /usr/bin/tr '\;' ' '", file)

            virtual_router = `#{cmd}`
            virtual_router.strip!

            # get some useful meta-data fields
            cmd = sprintf('wget -q -O - http://%s/latest/meta-data/instance_id', virtual_router)
            result = `#{cmd}`

            Facter.add('cloudstack_instance_id') do
                setcode { result }
            end
        end
    end
end
