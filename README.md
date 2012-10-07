# mysync.py
Python script for shortening rsync commands that are used frequently enough to be an annoyance. A lazy rsync, if you will.

## Use
<pre>mysync.py [target] [location] [direction] [behavior] [additional rsync flags]</pre>
The *target* and *location* arguments are shorthand aliases defined in the configuration file (which will be created from a template the first time that the script is run). See that file for instructions on how to set it up, or [the original blog post I wrote on it](http://blogofthedemitri.blogspot.com/2011/05/mydata-python-script-for-rsync.html).
<dl>
<dt>[target]</dt><dd>A path that exists both in the current location (i.e. the machine on which the script is being run) and at somewhere else, i.e. an external volume or remote host.</dd>
<dt>[location]</dt><dd>A "container" for targets, i.e. volume or host.</dd>
<dt>[direction]</dt><dd>Pull or push; pull updates the local copy according to content on the remote, push is vice versa.</dd>
<dt>[behavior]</dt><dd>Any of the following keywords (or part of one of them that uniquely matches one of them):
 <dl>
 <dt>ccc</dt><dd>Flags <tt>-c --delete-after</tt>; Makes the target a 100% carbon copy of the source, using checksum difference as the criterium for transferring rather than timestamp</dd>
 <dt>clean</dt><dd>Flags <tt>--delete-after --ignore-existing --existing</tt>; only deletes files in the target that are not in the source, and do nothing else (remove deleted files).</dd>
 <dt>copynew</dt><dd>Flags <tt>--ignore-existing</tt>; Skip files that exist already in target, copy new files.</dd>
 <dt>fullupdate</dt><dd>Flags <tt>-u</tt>; Update all files on the target, skip files that have been touched more recently on the source, and copy new files.</dd>
 <dt>update</dt><dd>Flags <tt>-u --existing</tt>; Update files that exist in both target and source such that the source copy is newer, but don't copy new files from the source.</dd>
 <dt>verbatim</dt><dd>Flags <tt>--delete-after</tt>; Make the target a 100% carbon copy of the source, using difference in file size or timestamp as the criterium for transferring.</dd>
 </dl></dd>
</dl>
