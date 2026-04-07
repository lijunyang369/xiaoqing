$listenPort = 18792
$targetHost = '127.0.0.1'
$targetPort = 9222
$listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Parse('0.0.0.0'), $listenPort)
$listener.Start()
Write-Output "PROXY_LISTENING=0.0.0.0:$listenPort -> $targetHost:$targetPort"
while ($true) {
  $client = $listener.AcceptTcpClient()
  Start-Job -ScriptBlock {
    param($client, $targetHost, $targetPort)
    try {
      $server = [System.Net.Sockets.TcpClient]::new($targetHost, $targetPort)
      $cs = $client.GetStream()
      $ss = $server.GetStream()
      $buf1 = New-Object byte[] 8192
      $buf2 = New-Object byte[] 8192
      $a = [System.Threading.Tasks.Task]::Run({
        param($from,$to,$buf)
        try { while (($n = $from.Read($buf,0,$buf.Length)) -gt 0) { $to.Write($buf,0,$n); $to.Flush() } } catch {}
      }.GetNewClosure(), @($cs,$ss,$buf1))
      $b = [System.Threading.Tasks.Task]::Run({
        param($from,$to,$buf)
        try { while (($n = $from.Read($buf,0,$buf.Length)) -gt 0) { $to.Write($buf,0,$n); $to.Flush() } } catch {}
      }.GetNewClosure(), @($ss,$cs,$buf2))
      [System.Threading.Tasks.Task]::WaitAny(@($a,$b)) | Out-Null
      $server.Close()
      $client.Close()
    } catch {
      try { $client.Close() } catch {}
    }
  } -ArgumentList $client,$targetHost,$targetPort | Out-Null
}
