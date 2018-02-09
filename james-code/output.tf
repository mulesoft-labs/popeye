output "object-store-int-dns-name" {
  value = "${aws_route53_record.object-store-int.fqdn}"
}
